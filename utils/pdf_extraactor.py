import os
import uuid
import fitz  # PyMuPDF for PDF processing
from typing import List, Dict
from dataclasses import dataclass, field
from kuzu_init import KuzuDBManager, Topic, Subtopic  # Import from your provided script

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
            raise FileNotFoundError(f"PDF file not found at {self.pdf_path}")
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

    def dummy_extract_topic(self, text: str) -> str:
        """Dummy function to extract the main topic from text (for testing)."""
        print("Extracting main topic from text.")
        lines = text.strip().split("\n")
        topic = lines[0] if lines else "Unnamed Topic"
        print(f"Extracted topic: {topic}")
        return topic

    def dummy_extract_subtopics(self, text: str) -> List[Dict[str, str]]:
        """Dummy function to extract subtopics from text (for testing)."""
        print("Extracting subtopics from text.")
        lines = text.strip().split("\n")[1:]  # Skip first line (topic)
        subtopics = []
        current_subtopic = {"name": "", "text": ""}
        
        for line in lines:
            if line.startswith("#"):  # Assuming '#' denotes a subtopic heading
                if current_subtopic["name"]:
                    subtopics.append(current_subtopic)
                current_subtopic = {"name": line.strip("# ").strip(), "text": ""}
            else:
                current_subtopic["text"] += line + "\n"
        
        if current_subtopic["name"]:
            subtopics.append(current_subtopic)
        
        print(f"Extracted {len(subtopics)} subtopics.")
        return subtopics if subtopics else [{"name": "Default Subtopic", "text": text}]

    def dummy_generate_bullet_points(self, text: str) -> List[str]:
        """Dummy function to generate bullet points from subtopic text."""
        print("Generating bullet points from subtopic text.")
        lines = text.strip().split("\n")
        bullet_points = [f"- {line.strip()}" for line in lines if line.strip()]
        print(f"Generated {len(bullet_points)} bullet points.")
        return bullet_points

    def build_knowledge_graph(self) -> None:
        """Extract topic/subtopics from PDF and build the knowledge graph."""
        print("Starting to build the knowledge graph.")
        
        # Extract text and images
        full_text, image_metadata = self.extract_text_and_images()

        # Extract main topic
        topic_name = self.dummy_extract_topic(full_text)
        topic_id = str(uuid.uuid4())
        print(f"Creating main topic with ID: {topic_id} and name: {topic_name}")
        main_topic = Topic(id=topic_id, name=topic_name)
        self.db_manager.create_topic(main_topic)

        # Extract subtopics
        subtopics_data = self.dummy_extract_subtopics(full_text)
        for position, subtopic_data in enumerate(subtopics_data):
            subtopic_id = str(uuid.uuid4())
            print(f"Creating subtopic {position + 1}/{len(subtopics_data)} with ID: {subtopic_id}")
            bullet_points = self.dummy_generate_bullet_points(subtopic_data["text"])
            
            # Split image metadata evenly among subtopics (for simplicity)
            images_per_subtopic = len(image_metadata) // max(1, len(subtopics_data))
            start_idx = position * images_per_subtopic
            end_idx = start_idx + images_per_subtopic if position < len(subtopics_data) - 1 else None
            subtopic_images = image_metadata[start_idx:end_idx]

            subtopic = Subtopic(
                id=subtopic_id,
                name=subtopic_data["name"],
                full_text=subtopic_data["text"],
                bullet_points=bullet_points,
                image_metadata=subtopic_images
            )
            self.db_manager.create_and_link_subtopic(topic_id, subtopic, position)
        
        print("Knowledge graph construction completed.")


# Example Usage
if __name__ == "__main__":
    # Assuming a sample PDF exists
    pdf_path = "Applied-Machine-Learning-and-AI-for-Engineers.pdf"
    print(f"Initializing knowledge graph creation for PDF: {pdf_path}")
    kg = PDFKnowledgeGraph(pdf_path=pdf_path, output_dir="./test_images")
    kg.build_knowledge_graph()
    print("Knowledge graph creation process finished.")