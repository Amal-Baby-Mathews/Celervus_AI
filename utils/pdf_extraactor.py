import asyncio
import json
import os
import uuid
import fitz  # PyMuPDF for PDF processing
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from kuzu_init import KuzuDBManager, Topic, Subtopic  # Import from your provided script
import re
import spacy
import aiohttp
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import pytextrank
from groq import Groq
from celerbud import BAMLFunctions  # Assuming BAMLFunctions is defined in baml.py
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
        # Instantiate BAMLFunctions
        self.baml = BAMLFunctions()
        """Initialize output directory and validate PDF path."""
        print(f"Initializing PDFKnowledgeGraph for PDF: {self.pdf_path}")


    def extract_text_and_images(self) -> tuple[str, List[Dict[str, str]]]:
        """Extract full text and images from the PDF, saving images to output_dir."""
        print(f"Opening PDF: {self.pdf_path}")
        if not os.path.exists(self.pdf_path):
             raise FileNotFoundError(f"PDF file not found at: {self.pdf_path}")

        try:
            doc = fitz.open(self.pdf_path)
        except Exception as e:
            print(f"Error opening PDF {self.pdf_path}: {e}")
            raise

        full_text = ""
        image_metadata = []

        # Ensure output directory exists before saving images
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created missing output directory: {self.output_dir}")

        for page_num in range(len(doc)):  # Replace enumerate(doc)
            page = doc[page_num]  # Explicitly access page by index
            print(f"Processing page {page_num + 1}/{len(doc)}")
            try:
                page_text = page.get_text("text") # type: ignore[attr-defined]
                if page_text:
                    full_text += page_text + "\n"
            except Exception as e:
                print(f"Warning: Could not extract text from page {page_num + 1}. Error: {e}")
                full_text += f"[Page {page_num + 1} text extraction failed]\n"


            # Extract images
            try:
                image_list = page.get_images(full=True)
            except Exception as e:
                print(f"Warning: Could not get images from page {page_num + 1}. Error: {e}")
                image_list = []

            for img_index, img in enumerate(image_list):
                print(f"Extracting image {img_index + 1} from page {page_num + 1}")
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image: # Check if extraction was successful
                         print(f"Warning: Failed to extract image data for xref {xref} on page {page_num + 1}")
                         continue
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_name = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}" # Page num 1-based
                    image_path = os.path.join(self.output_dir, image_name)

                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    image_metadata.append({
                        "image_path": image_path,
                        "image_name": image_name,
                        "page_number": str(page_num + 1) # Store 1-based page number
                    })
                except Exception as e:
                     print(f"Warning: Error processing image xref {xref} on page {page_num + 1}. Error: {e}")


        doc.close()
        print(f"Finished extracting text and images from PDF.")
        return full_text, image_metadata

    def generate_text_with_groq(self, prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
        """Generate text using Groq API with the given prompt."""
        # Consider making GROQ_API key retrieval more robust
        api_key = os.environ.get("GROQ_API")
        if not api_key:
            print("Error: GROQ_API environment variable not set.")
            # Decide on behavior: raise error or return empty string?
            # raise ValueError("GROQ_API environment variable not set.")
            return "[Groq API key missing]" # Return an indicator string

        # Use the actual Groq client or the dummy one if Groq isn't installed
        client = Groq(api_key=api_key)

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
                # max_tokens=200, # Be careful with limits, especially for bullet points
                max_tokens=400,  # Increased for potentially longer bullet point lists
                temperature=0.7,
            )
            content = chat_completion.choices[0].message.content
            result = content.strip() if content else "[No content returned by Groq API]"
            return result
        except Exception as e:
            print(f"Groq API error: {e}")
            # Consider more specific error handling based on potential Groq exceptions
            return f"[Groq API Error: {e}]" # Return error info

    def generate_title_with_groq(self, chunks: List[str]) -> str:
            """Generate a title using BAML instead of Groq API with the given text chunks."""
            print("Generating title with BAML.")
            if not chunks:
                print("Warning: No text chunks provided for title generation.")
                return "Unnamed Topic (No Input)"

            # Ensure chunks are strings and join them safely
            safe_chunks = " ".join([str(chunk) for chunk in chunks if chunk])
            if not safe_chunks.strip():
                print("Warning: Text chunks for title generation are empty after cleaning.")
                return "Unnamed Topic (Empty Input)"

            # Use specific BAML function with limited input
            title = self.baml.generate_document_title(text_chunks=safe_chunks[:2000])
            
            # Basic cleaning of the title
            title = title.strip().replace('"', '').replace("Title: ", "").replace("title: ", "")
            print(f"BAML generated title: {title}")
            return title if title else "Unnamed Topic (Generation Failed)"


    def generate_subtopic_name_with_groq(self, subtopic_text: str) -> str:
        """Generate a descriptive name for a subtopic using BAML instead of Groq API."""
        print("Generating subtopic name with BAML.")

        # Extract first 500 characters for context
        text_sample = subtopic_text[:500].strip()
        if not text_sample:
            print("Warning: Subtopic text sample is empty.")
            return "Unnamed Subtopic (Empty Input)"

        # Use specific BAML function
        name = self.baml.generate_subtopic_name(subtopic_text=text_sample)
        
        # Basic cleaning of the name
        name = name.strip('."').replace("Subtopic Name: ", "").replace("subtopic name: ", "")
        print(f"BAML generated subtopic name: {name}")
        return name if name else "Unnamed Subtopic (Generation Failed)"

    def extract_topic(self, doc: fitz.Document) -> str:
        """Extract the main topic by selecting chunks with larger fonts and using Groq."""
        print("Extracting main topic with PyMuPDF and Groq.")
        chunks = []
        try:
            for page_num in range(min(3, len(doc))):  # Limit to first 3 pages
                page = doc[page_num]
                blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"] # type: ignore[attr-defined]
                for block in blocks:
                    if block.get("type") == 0: # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                span_text = span.get("text", "").strip()
                                font_size = span.get("size", 10) # Default size
                                font_flags = span.get("flags", 0) # Default flags
                                is_bold = font_flags & (1 << 1) # Check bold flag (usually 2 or 16 depending on lib version)
                                is_larger = font_size > 12  # Larger font size threshold
                                is_short = 5 < len(span_text) < 100 # Filter very short/long strings

                                # Select text that is likely a title or heading
                                if span_text and is_short and (is_larger or is_bold) :
                                     # Simple check to avoid adding lines that are all caps (might be headers/footers)
                                     if not span_text.isupper() or len(span_text.split()) <= 5:
                                        chunks.append(span_text)
                                        print(f"  Found potential title chunk (Page {page_num + 1}, Size {font_size:.1f}, Bold: {is_bold}): {span_text}")
                                        if len(chunks) >= 5:  # Increased limit for more context
                                            break
                            if len(chunks) >= 5: break
                    if len(chunks) >= 5: break
                if len(chunks) >= 5: break

            # Fallback: If no specific chunks found, use the first few lines of the first page
            if not chunks:
                print("No prominent text chunks found, using first few lines as fallback.")
                page = doc[0]
                text = page.get_text("text")[:500]  # First 500 characters# type: ignore[attr-defined]
                # Split lines and filter empty ones
                first_lines = [line.strip() for line in text.split("\n") if line.strip()]
                chunks = first_lines[:5] # Take up to 5 non-empty lines

        except Exception as e:
            print(f"Error during text chunk extraction for topic: {e}")
            # Fallback if extraction fails entirely
            if not chunks:
                 try:
                     page = doc[0]
                     text = page.get_text("text")[:500]# type: ignore[attr-defined]
                     first_lines = [line.strip() for line in text.split("\n") if line.strip()]
                     chunks = first_lines[:5]
                 except Exception as fallback_e:
                      print(f"Error during fallback text extraction: {fallback_e}")
                      chunks = ["Document Content"] # Absolute fallback

        # Step 2: Call Groq to generate the topic
        try:
            topic = self.generate_title_with_groq(chunks)
        except Exception as e:
            print(f"Error generating title with Groq: {e}")
            topic = "Unnamed Topic (Error)"

        print(f"Final extracted topic: {topic}")
        return topic

    def extract_subtopics(self, doc: fitz.Document, text: str) -> List[Dict[str, Any]]:
        """Extract subtopics using PyMuPDF for structure, spaCy for validation, and embeddings for clustering."""
        print("Extracting subtopics from PDF.")
        headings = []
        current_text = ""
        current_heading = None
        last_page_processed = -1

        # Limit pages processed if needed (e.g., for very large docs or testing)
        # max_pages_for_subtopics = len(doc) # Process all pages by default
        max_pages_for_subtopics = min(50, len(doc)) # Or limit for testing
        print(f"Analyzing structure up to page {max_pages_for_subtopics} for subtopics...")

        # --- Structural Extraction (PyMuPDF + Heuristics) ---
        try:
            for page_num in range(max_pages_for_subtopics):
                last_page_processed = page_num
                page = doc[page_num]
                blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]# type: ignore[attr-defined]
                page_content_added = False # Track if content from this page was added

                for block in blocks:
                    if block.get("type") == 0: # Text block
                        block_text = ""
                        potential_heading = None
                        max_font_size = 0
                        is_block_bold = False

                        # First pass within the block to identify potential headings
                        for line in block.get("lines", []):
                             for span in line.get("spans", []):
                                span_text = span.get("text", "").strip()
                                if not span_text: continue

                                font_size = span.get("size", 10)
                                font_flags = span.get("flags", 0)
                                is_bold = font_flags & (1 << 1)
                                is_larger = font_size > 12.5 # Slightly increased threshold
                                is_short = 3 < len(span_text) < 100 # Sensible length for headings

                                # Heuristic for potential headings
                                if is_short and (is_larger or is_bold) and not span_text.isdigit():
                                     # Use spaCy for basic validation (check for nouns/proper nouns)
                                     doc_span = nlp(span_text)
                                     is_heading_like = any(token.pos_ in ["NOUN", "PROPN", "VERB"] for token in doc_span) and not span_text.isupper()

                                     if is_heading_like:
                                         # Keep the most prominent potential heading in the block
                                         if font_size > max_font_size or (font_size == max_font_size and is_bold and not is_block_bold):
                                              potential_heading = span_text
                                              max_font_size = font_size
                                              is_block_bold = is_bold
                                # Collect all text in the block
                                block_text += span_text + " "

                        block_text = block_text.strip()

                        # Process the identified potential heading
                        if potential_heading:
                            # If we have a current subtopic, save it before starting the new one
                            if current_heading and current_text.strip():
                                print(f"  Found heading: '{potential_heading}' on page {page_num + 1}")
                                headings.append({
                                    "name": current_heading["name"],
                                    "text": current_text.strip(),
                                    "start_page": current_heading["start_page"],
                                    "end_page": page_num # End page is the page *before* the new heading
                                })
                                current_text = "" # Reset text for the new subtopic

                            # Start the new subtopic
                            current_heading = {
                                "name": potential_heading,
                                "start_page": page_num + 1 # Use 1-based indexing
                            }
                            # Add the heading text itself to the start of the new subtopic text
                            current_text = potential_heading + "\n" + block_text[len(potential_heading):].strip() + "\n"
                            page_content_added = True
                        elif block_text:
                             # If it's not a heading block, append its text to the current subtopic
                             current_text += block_text + "\n"
                             page_content_added = True

                # Update end page if content was added and we have an active heading
                if page_content_added and current_heading:
                     current_heading["end_page"] = page_num + 1 # Current page is now the end page

            # Finalize the last subtopic after the loop
            if current_heading and current_text.strip():
                # If end_page wasn't updated on the very last loop iteration, set it
                if "end_page" not in current_heading:
                     current_heading["end_page"] = last_page_processed + 1
                headings.append({
                    "name": current_heading["name"],
                    "text": current_text.strip(),
                    "start_page": current_heading["start_page"],
                    "end_page": current_heading["end_page"]
                })
            elif not headings and text: # Handle case where no headings were found at all
                 print("No structural headings found. Treating entire document as one subtopic initially.")
                 headings.append({
                    "name": "Full Document Content",
                    "text": text.strip(),
                    "start_page": 1,
                    "end_page": len(doc)
                 })


        except Exception as e:
            print(f"Error during structural subtopic extraction: {e}")
            # Fallback if structural extraction fails but we have text
            if not headings and text:
                headings.append({
                    "name": "Full Document Content (Extraction Error)",
                    "text": text.strip(),
                    "start_page": 1,
                    "end_page": len(doc)
                })

        print(f"Found {len(headings)} potential subtopics structurally.")

        # --- Semantic Clustering (Optional Enhancement - can be complex) ---
        # This part is kept simpler for now, focusing on refining the structural ones.
        # A full implementation would involve clustering *all* text and merging/comparing
        # with structural headings, which adds significant complexity.

        # --- Refinement and Filtering ---
        subtopics = []
        processed_text_segments = set() # To avoid adding highly overlapping content

        for i, heading_data in enumerate(headings):
            subtopic_text = heading_data["text"]
            original_name = heading_data["name"]
            start_page = heading_data["start_page"]
            end_page = heading_data["end_page"]

            # Basic check for minimal content length
            if len(subtopic_text) < 100: # Skip very short sections
                 print(f"Skipping structurally found subtopic '{original_name}' due to short text ({len(subtopic_text)} chars).")
                 continue

             # Check for overlap (simple check based on start of text)
            text_start_key = subtopic_text[:100] # Key for checking overlap
            if text_start_key in processed_text_segments:
                 print(f"Skipping structurally found subtopic '{original_name}' due to detected overlap.")
                 continue
            processed_text_segments.add(text_start_key)


            # Generate a potentially better name using Groq if needed
            # Refine condition: generate if name is generic, too short/long, or seems like placeholder
            if (original_name.startswith("Topic ") or
                original_name == "Full Document Content" or
                len(original_name.split()) < 2 or
                len(original_name.split()) > 10 or
                original_name.isupper()): # Also regenerate if all caps
                print(f"Regenerating name for subtopic: '{original_name}'")
                refined_name = self.generate_subtopic_name_with_groq(subtopic_text)
            else:
                refined_name = original_name # Keep the structurally found name

            # Check relevance (can be costly, maybe optional or only for uncertain cases)
            # relevance_score = self.check_subtopic_relevance(subtopic_text)
            # if relevance_score < 0.5: # Adjust threshold as needed
            #     print(f"Skipping subtopic '{refined_name}' due to low relevance score: {relevance_score:.2f}")
            #     continue

            subtopics.append({
                "name": refined_name,
                "text": subtopic_text,
                "start_page": start_page,
                "end_page": end_page,
                "is_relevant": True # Assume relevant if it passed checks
            })
            print(f"  Added subtopic: '{refined_name}' (Pages {start_page}-{end_page})")


        # Step 4: Fallback if NO subtopics are found after all processing
        if not subtopics and text:
            print("No subtopics identified after filtering. Creating a single subtopic for the entire document.")
            name = self.generate_subtopic_name_with_groq(text[:1000])
            subtopics = [{
                "name": name,
                "text": text,
                "start_page": 1, # 1-based
                "end_page": len(doc),
                "is_relevant": True
            }]

        print(f"Extracted {len(subtopics)} final subtopics.")
        return subtopics


    def check_subtopic_relevance(self, text: str) -> float:
        """Check if a subtopic is relevant and substantial using BAML instead of Groq API."""
        # Take a sample of text if it's too long
        text_sample = text[:1000].strip() if len(text) > 1000 else text.strip()
        if len(text_sample) < 50:  # Too short to be relevant
            return 0.1

        try:
            # Use specific BAML function
            score = self.baml.check_subtopic_relevance(text=text_sample)
            score = max(0.0, min(1.0, score))  # Clamp score to [0.0, 1.0]
            print(f"  Relevance score: {score:.2f}")
            return score
        except Exception as e:
            print(f"Error checking subtopic relevance with BAML: {e}")
            return 0.5  # Default middle score on error


    async def generate_bullet_points_for_subtopic(self, subtopic_text: str) -> List[str]:
        """Generate bullet points for a single subtopic using BAML (Async helper)."""
        # Limit text length to avoid token limits and reduce cost/time
        text_to_summarize = subtopic_text[:3000].strip() if len(subtopic_text) > 3000 else subtopic_text.strip()

        if len(text_to_summarize) < 50:  # Not enough text to summarize
            return ["- Too short to summarize."]

        # Use BAML's extract_bullet_points (unchanged from previous version)
        try:
            bullet_points_response = self.baml.extract_bullet_points(text=text_to_summarize)
            bullet_points = bullet_points_response.points  # Extract the points array from BulletPoints object
            
            # Ensure bullet points start with "- "
            bullet_points = [f"- {bp.lstrip('- ')}" if not bp.startswith("- ") else bp for bp in bullet_points]
            return bullet_points if bullet_points else ["- No bullet points generated."]
        except Exception as e:
            print(f"Error generating bullet points with BAML: {e}")
            return ["- Error generating bullet points."]

    async def batch_generate_bullet_points(self, subtopics: List[Dict[str, Any]]) -> List[List[str]]:
        """Generate bullet points for multiple subtopics concurrently. (Async helper)"""
        # Note: BATCH_SIZE here controls concurrency of asyncio tasks,
        # not necessarily batching to the Groq API itself (unless the API supports it).
        BATCH_SIZE = 2  # Number of concurrent Groq calls
        all_bullet_points = []
        semaphore = asyncio.Semaphore(BATCH_SIZE) # Limit concurrency

        async def generate_with_semaphore(subtopic):
            async with semaphore:
                print(f"  Generating bullets for subtopic: {subtopic.get('name', 'Unnamed')[:30]}...")
                return await self.generate_bullet_points_for_subtopic(subtopic["text"])

        tasks = [generate_with_semaphore(subtopic) for subtopic in subtopics]
        results = await asyncio.gather(*tasks, return_exceptions=True) # Gather results, including potential errors

        # Process results, handling potential exceptions from gather
        for i, result in enumerate(results):
             if isinstance(result, Exception):
                  print(f"Error generating bullets for subtopic {i}: {result}")
                  all_bullet_points.append([f"- Error in async generation: {result}"])
             else:
                  all_bullet_points.append(result)

        return all_bullet_points

    # **** MODIFIED: Made async ****
    async def generate_bullet_points(self, subtopics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate bullet points from subtopic texts using Groq concurrently."""
        if not subtopics:
            print("No subtopics provided to generate bullet points for.")
            return []

        print(f"Generating bullet points for {len(subtopics)} subtopics...")

        # **** MODIFIED: Directly await the async helper ****
        # No need for asyncio.run() here!
        bullet_points_lists = await self.batch_generate_bullet_points(subtopics)

        # Check if the number of results matches the input
        if len(bullet_points_lists) != len(subtopics):
             print(f"Warning: Mismatch in number of bullet point lists ({len(bullet_points_lists)}) vs subtopics ({len(subtopics)}).")
             # Handle mismatch: either raise error or try to align based on available data
             # For now, we'll pad with error messages if necessary
             while len(bullet_points_lists) < len(subtopics):
                 bullet_points_lists.append(["- Error: Missing bullet point result."])
             # Or truncate if too many (less likely with gather)
             bullet_points_lists = bullet_points_lists[:len(subtopics)]


        # Attach bullet points to subtopics
        for i, bp_list in enumerate(bullet_points_lists):
            subtopics[i]["bullet_points"] = bp_list

        print(f"Finished generating bullet points for all subtopics.")
        return subtopics

    # **** MODIFIED: Made async and added max_subtopics parameter ****
    async def build_knowledge_graph(self, max_subtopics: Optional[int] = None) -> None:
        """
        Extract topic/subtopics from PDF and build the knowledge graph.

        Args:
            max_subtopics: Optional integer to limit the number of subtopics processed.
                           If None, all extracted subtopics are processed.
        """
        # Create output dir if it doesn't exist (moved here from build_knowledge_graph)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
        print("Starting to build the knowledge graph.")
        # Validate PDF path
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            raise ValueError(f"Invalid or non-existent PDF path: {self.pdf_path}")
        # Output directory is now created in __post_init__ or extract_text_and_images

        # Extract text and images
        full_text, image_metadata = self.extract_text_and_images()
        if not full_text and not image_metadata:
             print("Warning: PDF extraction yielded no text or images. Stopping graph build.")
             return # Stop if PDF seems empty or unreadable

        doc = None
        try:
            doc = fitz.open(self.pdf_path)

            # Extract main topic
            topic_name = self.extract_topic(doc)
            topic_id = str(uuid.uuid4())
            print(f"Creating main topic node with ID: {topic_id} and name: {topic_name}")
            main_topic = Topic(id=topic_id, name=topic_name)
            self.db_manager.create_topic(main_topic) # Assuming this is synchronous

            # Extract subtopics
            subtopics_data = self.extract_subtopics(doc, full_text)

            # --- Apply Subtopic Limit ---
            if max_subtopics is not None:
                original_count = len(subtopics_data)
                if original_count > max_subtopics:
                    print(f"Limiting subtopics from {original_count} to {max_subtopics}.")
                    subtopics_data = subtopics_data[:max_subtopics]
                else:
                    print(f"Requested subtopic limit ({max_subtopics}) is >= found subtopics ({original_count}). Processing all.")
            # --------------------------

            if not subtopics_data:
                 print("No subtopics found or remaining after filtering. Knowledge graph build stopped after creating main topic.")
                 return

            # Generate bullet points for the (potentially limited) subtopics
            # **** MODIFIED: await the async call ****
            subtopics_with_bullets = await self.generate_bullet_points(subtopics_data)

            print(f"Adding {len(subtopics_with_bullets)} subtopics to the knowledge graph...")
            for position, subtopic_data in enumerate(subtopics_with_bullets):
                subtopic_id = str(uuid.uuid4())
                subtopic_name = subtopic_data.get("name", f"Unnamed Subtopic {position + 1}")
                print(f"  Processing subtopic {position + 1}/{len(subtopics_with_bullets)}: '{subtopic_name[:50]}...' (ID: {subtopic_id})")

                # Assign images to subtopics based on page range
                start_page = subtopic_data.get("start_page", 0)
                end_page = subtopic_data.get("end_page", float('inf'))
                subtopic_images = []
                for img in image_metadata:
                    try:
                        img_page_num = int(img["page_number"]) # Ensure comparison is int vs int
                        # Check if image page number falls within the subtopic's page range
                        if start_page <= img_page_num <= end_page:
                            # --- CORRECTED URL CALCULATION ---

                            # Assume self.output_dir is like "./extracted_images/PdfSpecificFolder"
                            # The pdf_specific_folder_name is the part needed after /images/
                            pdf_specific_folder_name = os.path.basename(self.output_dir)

                            # The final URL should be /images/<pdf_specific_folder_name>/<image_name>
                            image_url = f"/images/{pdf_specific_folder_name}/{img['image_name']}"

                            # --- END CORRECTION ---

                            subtopic_images.append({
                                "image_path": img["image_path"], # Local server path
                                "image_name": img["image_name"],
                                "page_number": img["page_number"],
                                # Use the correctly constructed URL
                                "url": image_url
                            })
                    except ValueError:
                        print(f"Warning: Could not parse page number '{img.get('page_number')}' for image {img.get('image_name')}")
                    except Exception as e:
                         print(f"Warning: Error processing image metadata for subtopic: {e}")


                subtopic = Subtopic(
                    id=subtopic_id,
                    name=subtopic_name,
                    full_text=subtopic_data.get("text", "[No Text]"),
                    # Ensure bullet points exist, default to empty list
                    bullet_points=subtopic_data.get("bullet_points", []),
                    image_metadata=subtopic_images
                )
                # Assuming db_manager calls are synchronous
                self.db_manager.create_and_link_subtopic(topic_id, subtopic, position)

        except Exception as e:
             print(f"An error occurred during knowledge graph construction: {e}")
             # Optionally re-raise the exception if needed by the calling context
             # raise e
        finally:
            if doc:
                doc.close()
                print("Closed PDF document.")

        print("Knowledge graph construction process finished.")

    def get_all_topics(self) -> List[Dict[str, Any]]:
        try:
            response = self.db_manager.conn.execute("MATCH (t:Topic) RETURN t ORDER BY t.name")
            topics = []
            while response.has_next():# type: ignore[attr-defined]
                topic_data = response.get_next()[0]# type: ignore[attr-defined]
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

    def get_subtopic_details(self, subtopic_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.db_manager.conn.execute(
                "MATCH (s:Subtopic {id: $id}) RETURN s",
                {"id": subtopic_id}
            )
            if response.has_next():  # type: ignore[attr-defined]
                s_data = response.get_next()[0]  # type: ignore[attr-defined]
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
            if topic_response.has_next():  # type: ignore[attr-defined]
                t_data = topic_response.get_next()[0]  # type: ignore[attr-defined]
                topic = {
                    "id": t_data["id"],
                    "name": t_data["name"]
                }
            else:
                topic = None
            
            # Handle case where topic is None
            image_metadata = []
            if topic:
                image_metadata = [
                    {
                        "image_path": subtopic.image_metadata[i]["image_path"],
                        "image_name": subtopic.image_metadata[i]["image_name"],
                        "page_number": subtopic.image_metadata[i]["page_number"],
                        "url": f"/images/{topic['name']}/{subtopic.image_metadata[i]['image_name']}"
                    } for i in range(len(subtopic.image_metadata))
                ]
            else:
                print(f"Warning: No topic found for subtopic {subtopic_id}. Omitting topic name in image URLs.")
                image_metadata = [
                    {
                        "image_path": subtopic.image_metadata[i]["image_path"],
                        "image_name": subtopic.image_metadata[i]["image_name"],
                        "page_number": subtopic.image_metadata[i]["page_number"],
                        "url": f"/images/unknown_topic/{subtopic.image_metadata[i]['image_name']}"
                    } for i in range(len(subtopic.image_metadata))
                ]

            return {
                "subtopic": {
                    "id": subtopic.id,
                    "name": subtopic.name,
                    "full_text": subtopic.full_text,
                    "bullet_points": subtopic.bullet_points,
                    "image_metadata": image_metadata
                },
                "topic": topic
            }
        except Exception as e:
            print(f"Error retrieving subtopic details for subtopic {subtopic_id}: {e}")
            return None