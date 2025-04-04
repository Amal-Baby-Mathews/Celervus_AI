import asyncio
import json
import os
import uuid
import fitz  # PyMuPDF for PDF processing
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from kuzu_init import KuzuDBManager, Topic, Subtopic  # Import from your provided script

import spacy
import aiohttp
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import pytextrank
from groq import Groq
# Load spaCy model
nlp = spacy.load("en_core_web_md")
nlp.add_pipe("textrank")  # Add TextRank component to the pipeline
@dataclass
class PDFKnowledgeGraph:
    """Class to extract Topic and Subtopics from a PDF and build a knowledge graph."""
    pdf_path: str
    output_dir: str = "./extracted_images"
    db_manager: KuzuDBManager = field(default_factory=lambda: KuzuDBManager(db_path="./kuzu_db"))

    def __post_init__(self):
        """Initialize output directory and validate PDF path."""
        print(f"Initializing PDFKnowledgeGraph for PDF: {self.pdf_path}")


    def extract_text_and_images(self) -> tuple[str, List[Dict[str, str]]]:
        """Extract full text and images from the PDF, saving images to output_dir."""
        print(f"Opening PDF: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        full_text = ""
        image_metadata = []

        for page_num, page in enumerate(doc):
            print(f"Processing page {page_num + 1}/{len(doc)}")
            full_text += page.get_text("text") + "\n"
            
            # Extract images
            for img_index, img in enumerate(page.get_images(full=True)):
                print(f"Extracting image {img_index + 1} from page {page_num + 1}")
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_name = f"page_{page_num}_img_{img_index}.{image_ext}"
                image_path = os.path.join(self.output_dir, image_name)
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                image_metadata.append({
                    "image_path": image_path,
                    "image_name": image_name,
                    "page_number": str(page_num)
                })

        doc.close()
        print(f"Finished extracting text and images from PDF.")
        return full_text, image_metadata

    def generate_title_with_grok(self, chunks: List[str]) -> str:
        """Generate a title using Grok API with the given text chunks."""
        print("Generating title with Grok.")
        
        # Initialize Grok client
        client = Groq(api_key=os.environ.get("GROQ_API"))
        
        # Well-structured prompt
        prompt = (
            "You are a helpful AI assistant tasked with generating a concise title for a document. "
            "The title should be 5-10 words long, capturing the main theme of the text. "
            "Use the following text chunks from the document to determine the title:\n\n"
            f"{' '.join(chunks)}\n\n"
            "Provide only the title, without any additional explanation."
        )
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=50,
                temperature=0.7,
            )
            title = chat_completion.choices[0].message.content.strip()
            print(f"Grok generated title: {title}")
            return title if title else "Unnamed Topic"
        except Exception as e:
            print(f"Grok API error: {e}")
            return "Unnamed Topic"

    def extract_topic(self, doc: fitz.Document) -> str:
        """Extract the main topic by selecting chunks with larger fonts and using Grok."""
        print("Extracting main topic with PyMuPDF and Grok.")
        
        # Step 1: Extract text chunks with larger font sizes from the first few pages
        chunks = []
        for page_num in range(min(3, len(doc))):  # Limit to first 3 pages
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        span_text = span["text"].strip()
                        font_size = span["size"]
                        font_flags = span["flags"]
                        is_bold = font_flags & 2  # Check if bold
                        is_larger = font_size > 12  # Larger font size
                        is_short = len(span_text) < 100  # Short text, typical for headings
                        
                        # Select text that is likely a title or heading
                        if (is_larger or is_bold) and is_short and span_text:
                            chunks.append(span_text)
                            if len(chunks) >= 3:  # Limit to 3 chunks for context
                                break
                    if len(chunks) >= 3:
                        break
                if len(chunks) >= 3:
                    break
        
        # Fallback: If no chunks with larger fonts are found, use the first few lines
        if not chunks:
            page = doc[0]
            text = page.get_text("text")[:500]  # First 500 characters
            chunks = text.split("\n")[:3]  # First 3 lines
        
        # Step 2: Call Grok to generate the topic
        try:
            topic = self.generate_title_with_grok(chunks)
        except Exception as e:
            print(f"Error generating title with Grok: {e}")
            topic = "Unnamed Topic"
        
        print(f"Final extracted topic: {topic}")
        return topic
    def extract_subtopics(self, doc: fitz.Document, text: str) -> List[Dict[str, str]]:
        """Extract subtopics using PyMuPDF for structure, spaCy for validation, and embeddings for clustering."""
        print("Extracting subtopics from PDF.")
        
        # Step 1: Detect headings using PyMuPDF with improved heuristics
        headings = []
        current_text = ""
        page_ranges = []  # Track (start_page, end_page) for each subtopic
        current_heading = None
        
        # Fix the page range loop (limit to 50 pages for testing)
        for page_num in range(min(50, len(doc))):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        span_text = span["text"].strip()
                        font_size = span["size"]
                        font_flags = span["flags"]
                        is_bold = font_flags & 2  # Check if bold
                        is_larger = font_size > 12
                        is_short = len(span_text) < 100
                        
                        # Heuristic: Identify headings by font size, boldness, and length
                        if (is_larger or is_bold) and is_short:
                            # Validate with spaCy
                            doc_span = nlp(span_text)
                            is_heading_like = any(token.pos_ in ["NOUN", "PROPN"] for token in doc_span) and not span_text.isupper()
                            
                            if is_heading_like:
                                if current_text and current_heading:
                                    headings.append({
                                        "name": current_heading["name"],
                                        "text": current_text.strip(),
                                        "start_page": current_heading["start_page"],
                                        "end_page": page_num - 1
                                    })
                                current_heading = {
                                    "name": span_text,
                                    "start_page": page_num
                                }
                                page_ranges.append((page_num, page_num))
                                current_text = ""
                            else:
                                current_text += span_text + "\n"
                        else:
                            current_text += span_text + "\n"
            # Update end_page dynamically
            if current_heading and page_ranges:
                page_ranges[-1] = (page_ranges[-1][0], page_num)
        
        # Finalize the last subtopic
        if current_text and current_heading:
            headings.append({
                "name": current_heading["name"],
                "text": current_text.strip(),
                "start_page": current_heading["start_page"],
                "end_page": len(doc) - 1
            })
        
        # Step 2: Semantic clustering with embeddings for additional subtopics
        doc_nlp = nlp(text)
        sentences = [sent.text.strip() for sent in doc_nlp.sents if len(sent.text.strip()) > 10]
        
        if len(sentences) > 1:
            embedder = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = embedder.encode(sentences)
            num_clusters = min(len(sentences) // 5, len(headings) * 2) or 1
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            labels = kmeans.fit_predict(embeddings)
            
            # Group sentences by cluster
            clustered_subtopics = [[] for _ in range(num_clusters)]
            for sent, label in zip(sentences, labels):
                clustered_subtopics[label].append(sent)
            
            # Combine structural headings with semantic clusters
            semantic_subtopics = []
            for i, cluster in enumerate(clustered_subtopics):
                cluster_text = " ".join(cluster)
                if cluster_text:
                    # Estimate page range for the cluster (approximate)
                    start_idx = text.find(cluster_text[:50])
                    end_idx = start_idx + len(cluster_text)
                    start_page = max(0, sum(1 for _ in text[:start_idx].split("\n")) // 50)  # Rough estimate
                    end_page = min(len(doc) - 1, sum(1 for _ in text[:end_idx].split("\n")) // 50)
                    semantic_subtopics.append({
                        "name": f"Topic {i + 1}",
                        "text": cluster_text,
                        "start_page": start_page,
                        "end_page": end_page
                    })
        
        # Step 3: Merge structural and semantic subtopics
        subtopics = []
        for heading in headings:
            subtopics.append({
                "name": heading["name"],
                "text": heading["text"],
                "start_page": heading["start_page"],
                "end_page": heading["end_page"]
            })
        
        # Add semantic subtopics if they provide additional value
        for semantic_sub in semantic_subtopics:
            # Avoid duplicates by checking overlap with structural subtopics
            overlap = False
            for sub in subtopics:
                if (semantic_sub["start_page"] <= sub["end_page"] and semantic_sub["end_page"] >= sub["start_page"] and
                    semantic_sub["text"][:50] in sub["text"]):
                    overlap = True
                    break
            if not overlap:
                subtopics.append(semantic_sub)
        
        # Step 4: Fallback if no subtopics are found
        if not subtopics:
            subtopics = [{"name": "Default Subtopic", "text": text, "start_page": 0, "end_page": len(doc) - 1}]
        
        print(f"Extracted {len(subtopics)} subtopics.")
        return subtopics

    def generate_bullet_points(self, text: str) -> List[str]:
        """Generate bullet points from subtopic text using Grok."""
        print("Generating bullet points with Grok.")
        
        # Placeholder for Grok integration
        # async def generate_with_grok(text: str) -> List[str]:
        #     prompt = f"Summarize the following text into concise bullet points:\n\n{text}"
        #     response = await grok.create(prompt=prompt, max_tokens=200)
        #     bullet_points = response.choices[0].text.strip().split("\n")
        #     return [bp.strip() for bp in bullet_points if bp.strip()]
        #
        # bullet_points = asyncio.run(generate_with_grok(text))
        
        # Placeholder text to signify Grok integration
        bullet_points = ["- Placeholder bullet point 1", "- Placeholder bullet point 2"]
        
        print(f"Generated {len(bullet_points)} bullet points.")
        return bullet_points

    def build_knowledge_graph(self) -> None:
        """Extract topic/subtopics from PDF and build the knowledge graph."""
        print("Starting to build the knowledge graph.")
        # Validate PDF path and output directory
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            raise ValueError(f"Invalid PDF path: {self.pdf_path}")
        if not self.output_dir:
            raise ValueError("Output directory cannot be null.")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        # Extract text and images
        full_text, image_metadata = self.extract_text_and_images()
        doc = fitz.open(self.pdf_path)

        # Extract main topic
        topic_name = self.extract_topic(doc)
        topic_id = str(uuid.uuid4())
        print(f"Creating main topic with ID: {topic_id} and name: {topic_name}")
        main_topic = Topic(id=topic_id, name=topic_name)
        self.db_manager.create_topic(main_topic)

        # Extract subtopics
        subtopics_data = self.extract_subtopics(doc, full_text)
        for position, subtopic_data in enumerate(subtopics_data):
            subtopic_id = str(uuid.uuid4())
            print(f"Creating subtopic {position + 1}/{len(subtopics_data)} with ID: {subtopic_id}")
            bullet_points = self.generate_bullet_points(subtopic_data["text"])
            
            # Assign images to subtopics based on page range and define URL here
            start_page = subtopic_data["start_page"]
            end_page = subtopic_data["end_page"]
            subtopic_images = [
                {
                    "image_path": img["image_path"],
                    "image_name": img["image_name"],
                    "page_number": img["page_number"],
                    "url": f"/images/{os.path.basename(self.output_dir)}/{img['image_name']}"
                } for img in image_metadata
                if start_page <= int(img["page_number"]) <= end_page
            ]

            subtopic = Subtopic(
                id=subtopic_id,
                name=subtopic_data["name"],
                full_text=subtopic_data["text"],
                bullet_points=bullet_points,
                image_metadata=subtopic_images
            )
            self.db_manager.create_and_link_subtopic(topic_id, subtopic, position)
        
        doc.close()
        print("Knowledge graph construction completed.")
    def get_all_topics(self) -> List[Dict[str, Any]]:
        try:
            response = self.db_manager.conn.execute("MATCH (t:Topic) RETURN t ORDER BY t.name")
            topics = []
            while response.has_next():
                topic_data = response.get_next()[0]
                topics.append({"id": topic_data["id"], "name": topic_data["name"]})
            return topics
        except Exception as e:
            print(f"Error retrieving topics: {e}")
            return []

    def get_topic_details(self, topic_id: str) -> Optional[Dict[str, Any]]:
        try:
            topic = self.db_manager.get_topic(topic_id)
            if not topic:
                return None
            subtopics = self.db_manager.get_subtopics(topic_id)
            return {
                "id": topic.id,
                "name": topic.name,
                "subtopics": [
                    {
                        "id": subtopic.id,
                        "name": subtopic.name,
                        "full_text": subtopic.full_text,
                        "bullet_points": subtopic.bullet_points,
                        "image_metadata": [
                            {
                                "image_path": img["image_path"],
                                "image_name": img["image_name"],
                                "page_number": img["page_number"],
                                "url": img["url"]
                            } for img in subtopic.image_metadata
                        ]
                    } for subtopic in subtopics
                ]
            }
        except Exception as e:
            print(f"Error retrieving topic {topic_id}: {e}")
            return None

    def get_subtopic_details(self, subtopic_id: str) -> Optional[Dict[str, any]]:
        try:
            response = self.db_manager.conn.execute(
                "MATCH (s:Subtopic {id: $id}) RETURN s",
                {"id": subtopic_id}
            )
            if response.has_next():
                s_data = response.get_next()[0]
                subtopic = Subtopic(
                    id=s_data["id"],
                    name=s_data["name"],
                    full_text=s_data["text"],
                    bullet_points=s_data["bullet_points"],
                    image_metadata=json.loads(s_data["image_metadata"])
                )
            else:
                return None
            
            topic_response = self.db_manager.conn.execute(
                "MATCH (s:Subtopic {id: $id})-[:SUBTOPIC_OF]->(t:Topic) RETURN t",
                {"id": subtopic_id}
            )
            if topic_response.has_next():
                t_data = topic_response.get_next()[0]
                topic = {
                    "id": t_data["id"],
                    "name": t_data["name"]
                }
            else:
                topic = None
            
            return {
                "subtopic": {
                    "id": subtopic.id,
                    "name": subtopic.name,
                    "full_text": subtopic.full_text,
                    "bullet_points": subtopic.bullet_points,
                    "image_metadata": [
                        {
                            "image_path": subtopic.image_metadata[i]["image_path"],
                            "image_name": subtopic.image_metadata[i]["image_name"],
                            "page_number": subtopic.image_metadata[i]["page_number"],
                            "url": f"/images/{t_data["name"]}/{subtopic.image_metadata[i]['image_name']}"
                        } for i in range(len(subtopic.image_metadata))
                    ]
                },
                "topic": topic
            }
        except Exception as e:
            print(f"Error retrieving subtopic details for subtopic {subtopic_id}: {e}")
            return None

