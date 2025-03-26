import PyPDF2
from typing import List, Optional, Dict
from dataclasses import dataclass, field
import os
import re
import json
import PIL.Image
import io
from groq import Groq
from dotenv import load_dotenv

# Assuming KuzuDBManager is imported from another module
from kuzu_init import KuzuDBManager, Topic as KuzuTopic, Subtopic as KuzuSubtopic

@dataclass
class Topic:
    """Represents a topic in the PDF with hierarchical structure."""
    title: str
    page_start: int
    page_end: Optional[int] = None
    level: int = 0
    children: List['Topic'] = field(default_factory=list)

@dataclass
class TopicContent:
    """Stores comprehensive content for a topic."""
    title: str
    page_start: int
    page_end: int
    full_text: str = ""
    bullet_points: List[str] = field(default_factory=list)
    flashcards: List[Dict] = field(default_factory=list)
    image_metadata: List[Dict[str, str]] = field(default_factory=list)
    subtopics: List['TopicContent'] = field(default_factory=list)

class PDFKuzuExtractor:
    """Extracts topics and subtopics from a PDF and stores them in Kuza DB using Groq for content generation."""
    
    def __init__(self, pdf_path: str, db_path: str = "./kuzu_db", output_dir: Optional[str] = None):
        """
        Initialize the extractor with PDF path, Kuza DB path, and output directory.

        :param pdf_path: Path to the PDF file.
        :param db_path: Path to the Kuza DB directory.
        :param output_dir: Directory to save extracted images (optional).
        """
        load_dotenv()
        self.pdf_path = pdf_path
        self.db_manager = KuzuDBManager(db_path=db_path, in_memory=False)
        self.output_dir = output_dir or os.path.join(os.path.dirname(pdf_path), 'extracted_content')
        os.makedirs(self.output_dir, exist_ok=True)
        self.pdf_reader = None
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.total_pages = 0

    def load_pdf(self) -> bool:
        """Load the PDF file and initialize the reader."""
        try:
            with open(self.pdf_path, 'rb') as file:
                self.pdf_reader = PyPDF2.PdfReader(file)
                self.total_pages = len(self.pdf_reader.pages)
            return True
        except FileNotFoundError:
            print(f"Error: File {self.pdf_path} not found.")
            return False
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False

    def extract_outline(self) -> List[Dict]:
        """Extract the outline from the PDF."""
        if not self.pdf_reader:
            print("PDF not loaded. Call load_pdf() first.")
            return []
        try:
            if not hasattr(self.pdf_reader, 'outline') or not self.pdf_reader.outline:
                print("No outline found. Using alternative extraction.")
                return self._extract_outline_alternative()
            outline = self.pdf_reader.outline
            processed_outline = []

            def process_outline_item(item, current_level=0):
                if isinstance(item, list):
                    for sub_item in item:
                        process_outline_item(sub_item, current_level)
                elif hasattr(item, 'title'):
                    page = self._get_page_number(item)
                    if page is not None:
                        processed_outline.append({'title': item.title, 'page': page, 'level': current_level})
                    if hasattr(item, 'children'):
                        process_outline_item(item.children, current_level + 1)

            process_outline_item(outline)
            return processed_outline
        except Exception as e:
            print(f"Error extracting outline: {e}")
            return []

    def _get_page_number(self, item) -> Optional[int]:
        """Safely get page number for an outline item."""
        try:
            return self.pdf_reader.get_destination_page_number(item)
        except Exception:
            return None

    def _extract_outline_alternative(self) -> List[Dict]:
        """Alternative method to extract topics when no outline exists."""
        processed_outline = []
        for page_num in range(min(10, self.total_pages)):
            try:
                page = self.pdf_reader.pages[page_num]
                text = page.extract_text().split('\n')[0]
                if text.strip() and len(text.split()) > 2:
                    processed_outline.append({'title': text[:50] + '...', 'page': page_num, 'level': 0})
            except Exception as e:
                print(f"Error extracting alternative outline: {e}")
        return processed_outline

    def build_topic_hierarchy(self, outline_items: List[Dict]) -> List[Topic]:
        """Build a hierarchical topic structure from outline items."""
        if not outline_items:
            return []
        sorted_items = sorted(outline_items, key=lambda x: x['page'])
        topics, stack = [], []
        for item in sorted_items:
            while stack and stack[-1].level >= item['level']:
                stack.pop()
            topic = Topic(title=item['title'], page_start=item['page'], level=item['level'])
            if stack:
                stack[-1].children.append(topic)
            else:
                topics.append(topic)
            stack.append(topic)
        self._assign_page_ranges(topics)
        return topics

    def _assign_page_ranges(self, topics: List[Topic]):
        """Assign page ranges to topics based on hierarchy."""
        def assign_ranges(topics_list: List[Topic], max_page: int):
            for i, topic in enumerate(topics_list):
                next_topic_start = max_page
                for j in range(i + 1, len(topics_list)):
                    if topics_list[j].level <= topic.level:
                        next_topic_start = topics_list[j].page_start
                        break
                topic.page_end = min(next_topic_start - 1, max_page)
                if topic.children:
                    assign_ranges(topic.children, topic.page_end)
        assign_ranges(topics, self.total_pages)

    def extract_content_recursively(self, topics: List[Topic]) -> List[TopicContent]:
        """Recursively extract content for topics and subtopics."""
        topic_contents = []
        with open(self.pdf_path, 'rb') as file:
            self.pdf_reader = PyPDF2.PdfReader(file)
            for topic in topics:
                topic_content = self._extract_topic_content(topic)
                topic_contents.append(topic_content)
        return topic_contents

    def _extract_topic_content(self, topic: Topic) -> TopicContent:
        """Extract comprehensive content for a single topic."""
        topic_dir = os.path.join(self.output_dir, self._sanitize_filename(topic.title))
        os.makedirs(topic_dir, exist_ok=True)
        full_text = self._extract_text_from_page_range(topic.page_start, topic.page_end)
        image_paths = self._extract_images_from_page_range(topic.page_start, topic.page_end, topic_dir)
        image_metadata = [{"image_path": path, "image_name": os.path.basename(path)} for path in image_paths]
        bullet_points = self._generate_bullet_points(full_text)
        flashcards = self._generate_flashcards(full_text)
        subtopic_contents = [self._extract_topic_content(subtopic) for subtopic in topic.children]
        if subtopic_contents:
            full_text += "\n\n" + "\n\n".join([st.full_text for st in subtopic_contents])
        return TopicContent(
            title=topic.title,
            page_start=topic.page_start,
            page_end=topic.page_end,
            full_text=full_text,
            bullet_points=bullet_points,
            flashcards=flashcards,
            image_metadata=image_metadata,
            subtopics=subtopic_contents
        )

    def _extract_text_from_page_range(self, start_page: int, end_page: int) -> str:
        """Extract text from a specific page range."""
        text_parts = []
        for page_num in range(start_page, end_page + 1):
            try:
                page = self.pdf_reader.pages[page_num]
                text_parts.append(page.extract_text())
            except Exception as e:
                print(f"Error extracting text from page {page_num}: {e}")
        return "\n".join(text_parts)

    def _extract_images_from_page_range(self, start_page: int, end_page: int, output_dir: str) -> List[str]:
        """Extract images from a specific page range."""
        image_paths = []
        for page_num in range(start_page, end_page + 1):
            try:
                page = self.pdf_reader.pages[page_num]
                for img_index, img_obj in enumerate(page.images):
                    try:
                        img_data = img_obj.data
                        img = PIL.Image.open(io.BytesIO(img_data))
                        img_filename = f"page_{page_num}_img_{img_index}.png"
                        img_path = os.path.join(output_dir, img_filename)
                        img.save(img_path)
                        image_paths.append(img_path)
                    except Exception as e:
                        print(f"Error saving image from page {page_num}: {e}")
            except Exception as e:
                print(f"Error extracting images from page {page_num}: {e}")
        return image_paths

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters."""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)[:255]

    def _generate_bullet_points(self, text: str, max_length: int = 500) -> List[str]:
        """Generate bullet points using Groq."""
        text = text[:max_length]
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": f"Summarize the following text into concise bullet points:\n\n{text}"}],
                model="llama-3.1-70b-versatile"
            )
            return [point.strip() for point in response.choices[0].message.content.split('\n') if point.strip()]
        except Exception as e:
            print(f"Groq Bullet Point Generation Error: {e}")
            return []

    def _generate_flashcards(self, text: str, max_length: int = 500) -> List[Dict]:
        """Generate flashcards using Groq."""
        text = text[:max_length]
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": f"Generate flashcards from the following text. Each flashcard should have a question and an answer:\n\n{text}"}],
                model="llama-3.1-70b-versatile"
            )
            flashcards_text = response.choices[0].message.content
            return [{"question": card[0].strip(), "answer": card[1].strip()} 
                    for card in re.findall(r'Q:(.*?)\nA:(.*?)(?=\n\n|$)', flashcards_text, re.DOTALL)]
        except Exception as e:
            print(f"Groq Flashcard Generation Error: {e}")
            return []

    def vectorize_topics_and_subtopics(self, topic_contents: List[TopicContent]) -> None:
        """Dummy function to vectorize topic and subtopic names against IDs (to be implemented)."""
        for topic_content in topic_contents:
            topic_id = f"topic_{hash(topic_content.title)}"
            print(f"Vectorizing Topic: {topic_id} - {topic_content.title}")
            for subtopic_content in topic_content.subtopics:
                subtopic_id = f"subtopic_{hash(subtopic_content.title)}"
                print(f"Vectorizing Subtopic: {subtopic_id} - {subtopic_content.title}")
        print("Vectorization placeholder - implement embedding logic here.")

    def process_and_store(self) -> None:
        """Extract topics, generate content, and store in Kuza DB."""
        if not self.load_pdf():
            return
        topics = self.build_topic_hierarchy(self.extract_outline())
        if not topics:
            print("No topics extracted.")
            return
        topic_contents = self.extract_content_recursively(topics)
        self.vectorize_topics_and_subtopics(topic_contents)
        
        for topic_content in topic_contents:
            topic_id = f"topic_{hash(topic_content.title)}"
            topic = KuzuTopic(
                id=topic_id,
                name=topic_content.title,
                full_text=topic_content.full_text,
                bullet_points=topic_content.bullet_points,
                image_metadata=topic_content.image_metadata,
                embedding=[0.0] * 1536  # Dummy embedding
            )
            self.db_manager.create_topic(topic)
            
            for subtopic_content in topic_content.subtopics:
                subtopic_id = f"subtopic_{hash(subtopic_content.title)}"
                subtopic = KuzuSubtopic(
                    id=subtopic_id,
                    name=subtopic_content.title,
                    full_text=subtopic_content.full_text,
                    bullet_points=subtopic_content.bullet_points,
                    image_metadata=subtopic_content.image_metadata,
                    embedding=[0.0] * 1536  # Dummy embedding
                )
                self.db_manager.create_and_link_subtopic(topic_id, subtopic, order=len(topic_content.subtopics))

        print(f"Content processed and stored in Kuza DB at {self.db_manager.db_path}")

# Example Usage
if __name__ == "__main__":
    pdf_path = "path/to/your/pdf.pdf"
    extractor = PDFKuzuExtractor(pdf_path)
    extractor.process_and_store()