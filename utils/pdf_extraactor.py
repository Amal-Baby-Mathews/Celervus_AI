import asyncio
import json
import os
import uuid
import fitz  # PyMuPDF for PDF processing
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from kuzu_init import KuzuDBManager, Topic, Subtopic  # Import from your provided script
from fastapi import FastAPI, File, UploadFile
import uvicorn
import spacy
import aiohttp
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import pytextrank
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
        if not os.path.exists(self.pdf_path):
            print("Not using a PDF for querying")
        if not os.path.exists(self.output_dir):
            print(f"Output directory {self.output_dir} does not exist. Creating it.")
            os.makedirs(self.output_dir)

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

    async def generate_title_with_grok(chunks: List[str]) -> str:
        """Generate a title using Grok API with the given text chunks."""
        print("Generating title with Grok.")
        prompt = "Generate a concise title (5-10 words) for the following text:\n\n" + "\n".join(chunks)
        # Get Grok API key from environment
        GROQ_API_KEY = os.getenv("GROQ_API")
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.grok.ai/v1/generate",  # Replace with actual Grok API endpoint
                json={
                    "prompt": prompt,
                    "max_tokens": 50,
                    "temperature": 0.7
                },
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
            ) as response:
                if response.status != 200:
                    print(f"Grok API error: {response.status}")
                    return "Unnamed Topic"
                result = await response.json()
                title = result.get("choices", [{}])[0].get("text", "Unnamed Topic").strip()
                print(f"Grok generated title: {title}")
                return title if title else "Unnamed Topic"

    def extract_topic(self, text: str) -> str:
        """Extract the main topic using spaCy, falling back to Grok if not applicable."""
        print("Extracting main topic with spaCy and TextRank.")
        doc = nlp(text[:5000])  # First 5000 characters for context
        
        # Step 1: Try spaCy with TextRank
        key_phrases = [phrase.text for phrase in doc._.phrases if len(phrase.text.split()) <= 5]
        spacy_topic = key_phrases[0] if key_phrases else "Unnamed Topic"
        
        # Step 2: Evaluate if spaCy topic is applicable
        generic_phrases = {"introduction", "chapter", "section", "unnamed topic"}
        is_applicable = (
            len(spacy_topic.split()) > 1 and  # Not too short
            spacy_topic.lower() not in generic_phrases and  # Not generic
            any(token.pos_ in ["NOUN", "PROPN"] for token in nlp(spacy_topic))  # Contains meaningful words
        )
        
        if is_applicable:
            print(f"spaCy extracted topic: {spacy_topic}")
            return spacy_topic
        
        # Step 3: Fall back to Grok if spaCy topic is not applicable
        print("spaCy topic not applicable, falling back to Grok.")
        
        # Select key text chunks for Grok
        # Option 1: First few paragraphs (split by double newlines)
        paragraphs = text[:5000].split("\n\n")
        chunks = paragraphs[:3] if len(paragraphs) >= 3 else paragraphs  # First 3 paragraphs
        
        # Option 2: Key sentences using TextRank
        key_sentences = [sent.text for sent in doc._.textrank.summary(limit_sentences=3)]
        if len(" ".join(key_sentences)) > 200:  # Ensure enough context
            chunks = key_sentences
        
        # Call Grok API asynchronously
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If running in an async context (e.g., FastAPI), use await
                topic = loop.run_until_complete(self.generate_title_with_grok(chunks))
            else:
                # Otherwise, run in a new loop
                topic = asyncio.run(self.generate_title_with_grok(chunks))
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
        
        # Extract text and images
        full_text, image_metadata = self.extract_text_and_images()
        doc = fitz.open(self.pdf_path)

        # Extract main topic
        topic_name = self.extract_topic(full_text)
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
            
            # Assign images to subtopics based on page range
            start_page = subtopic_data["start_page"]
            end_page = subtopic_data["end_page"]
            subtopic_images = [
                img for img in image_metadata
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
    def get_all_topics(self) -> List[Dict[str, any]]:
        """
        Retrieve all topics with their subtopics for frontend display.

        :return: List of dictionaries containing topic details and their subtopics.
        """
        try:
            response = self.db_manager.conn.execute("MATCH (t:Topic) RETURN t ORDER BY t.name")
            topics = []
            while response.has_next():
                topic_data = response.get_next()[0]
                topic_id = topic_data["id"]
                topic = self.db_manager.get_topic(topic_id)
                if topic:
                    subtopics = self.db_manager.get_subtopics(topic_id)
                    topics.append({
                        "id": topic.id,
                        "name": topic.name,
                        "subtopics": [
                            {
                                "id": subtopic.id,
                                "name": subtopic.name,
                                "full_text": subtopic.full_text,
                                "bullet_points": subtopic.bullet_points,
                                "image_metadata": subtopic.image_metadata
                            } for subtopic in subtopics
                        ]
                    })
            return topics
        except Exception as e:
            print(f"Error retrieving all topics: {e}")
            return []

    def get_topic_details(self, topic_id: str) -> Optional[Dict[str, any]]:
        """
        Retrieve a specific topic and its subtopics by topic ID for frontend display.

        :param topic_id: ID of the topic to retrieve.
        :return: Dictionary containing topic details and its subtopics, or None if not found.
        """
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
                        "image_metadata": subtopic.image_metadata
                    } for subtopic in subtopics
                ]
            }
        except Exception as e:
            print(f"Error retrieving topic details for topic {topic_id}: {e}")
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
                        "image_metadata": subtopic.image_metadata
                    },
                    "topic": topic
                }
            except Exception as e:
                print(f"Error retrieving subtopic details for subtopic {subtopic_id}: {e}")
                return None

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.post("/create_graph")
async def create_graph(file: UploadFile = File(...)):
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    pdf_path = os.path.join(uploads_dir, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    
    pdf_name = os.path.basename(file.filename).split(".")[0]
    output_dir = f"./extracted_images/{pdf_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    kg = PDFKnowledgeGraph(pdf_path=pdf_path, output_dir=output_dir)
    kg.build_knowledge_graph()
    return {"message": "Graph created successfully"}

@app.get("/topics")
def get_all_topics():
    kg = PDFKnowledgeGraph(pdf_path="dummy_path", output_dir="dummy_dir")
    topics = kg.get_all_topics()
    return topics

@app.get("/topics/{topic_id}")
def get_topic_details(topic_id: str):
    kg = PDFKnowledgeGraph(pdf_path="dummy_path", output_dir="dummy_dir")
    details = kg.get_topic_details(topic_id)
    return details

@app.get("/subtopics/{subtopic_id}")
def get_subtopic_details(subtopic_id: str):
    kg = PDFKnowledgeGraph(pdf_path="dummy_path", output_dir="dummy_dir")
    details = kg.get_subtopic_details(subtopic_id)
    return details
# Example Usage
if __name__ == "__main__":
    # Commenting out the example usage and serving the FastAPI app
    # Assuming a sample PDF exists
    # pdf_path = "Applied-Machine-Learning-and-AI-for-Engineers.pdf"
    # print(f"Initializing knowledge graph creation for PDF: {pdf_path}")
    # kg = PDFKnowledgeGraph(pdf_path=pdf_path, output_dir="./test_images")
    # kg.build_knowledge_graph()
    # print("Knowledge graph creation process finished.")

    uvicorn.run(app, host="0.0.0.0", port=8008)