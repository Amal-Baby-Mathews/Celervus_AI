import kuzu
import json
from typing import Optional, List, Dict, Any
from langchain_kuzu.graphs.kuzu_graph import KuzuGraph
from langchain_kuzu.chains.graph_qa.kuzu import KuzuQAChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from dataclasses import dataclass, field

@dataclass
class Topic:
    """Represents a main topic with content and metadata."""
    id: str
    name: str # Name of the topic (Main Topic of the entire pdf)


@dataclass
class Subtopic:#Individual topics inside the pdf
    """Represents a subtopic linked to a main topic with content and metadata."""
    id: str
    name: str
    full_text: str
    bullet_points: List[str] = field(default_factory=list)
    image_metadata: List[Dict[str, str]] = field(default_factory=list)

class KuzuDBManager:
    """Manages a local Kuza database with topic/subtopic creation and querying."""
    
    def __init__(self, db_path: str = "./kuzu_db", in_memory: bool = False):
        """
        Initialize the Kuza DB manager.

        :param db_path: Path to the database directory (ignored if in_memory is True).
        :param in_memory: If True, creates an in-memory database; otherwise, uses disk storage.
        """
        load_dotenv()
        self.db_path = ":memory:" if in_memory else db_path
        self.db = kuzu.Database(self.db_path)
        self.conn = kuzu.Connection(self.db)
        self.graph = KuzuGraph(self.db, allow_dangerous_requests=True)
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API"), model_name="llama3-70b-8192")
        self.qa_chain = KuzuQAChain.from_llm(llm=self.llm, graph=self.graph, verbose=True, allow_dangerous_requests=True)
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        """Initialize the database schema with Topic, Subtopic, and relationship tables."""
        try:
            self.conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS Topic(
                    id STRING,
                    name STRING,
                    PRIMARY KEY (id)
                );
            """)
        except Exception as e:
            print(f"Error creating Topic table: {e}")

        try:
            self.conn.execute("""
                CREATE NODE TABLE IF NOT EXISTS Subtopic(
                    id STRING,
                    name STRING,
                    text STRING,
                    bullet_points STRING[],
                    image_metadata STRING,
                    PRIMARY KEY (id)
                );
            """)
        except Exception as e:
            print(f"Error creating Subtopic table: {e}")

        try:
            self.conn.execute("""
                CREATE REL TABLE IF NOT EXISTS SUBTOPIC_OF(
                    FROM Subtopic TO Topic,
                    position UINT32
                );
            """)
        except Exception as e:
            print(f"Error creating SUBTOPIC_OF relationship table: {e}")

    def create_topic(self, topic: Topic) -> bool:
        """
        Create a new topic in the database.

        :param topic: Topic object with id, name, full_text, bullet_points, image_metadata.
        :return: True if successful, False otherwise.
        """
        try:
            self.conn.execute(
                """
                MERGE (t:Topic {id: $id})
                ON MATCH SET t.name = $name
                ON CREATE SET t.name = $name
                """,
                {
                    "id": topic.id,
                    "name": topic.name,
                }
            )
            return True
        except Exception as e:
            print(f"Error creating topic {topic.id}: {e}")
            return False

    def create_and_link_subtopic(self, parent_topic_id: str, subtopic: Subtopic, position: int = 0) -> bool:
        """
        Create a subtopic and link it to a parent topic in one operation.

        :param parent_topic_id: ID of the parent topic.
        :param subtopic: Subtopic object with id, name, full_text, bullet_points, image_metadata.
        :param position: Order of the subtopic within the topic (default 0).
        :return: True if successful, False otherwise.
        """
        try:
            image_metadata_json = json.dumps(subtopic.image_metadata)
            self.conn.execute(
                """
                MATCH (t:Topic {id: $topic_id})
                MERGE (s:Subtopic {id: $subtopic_id})
                ON MATCH SET s.name = $name, s.text = $text, s.bullet_points = $bullet_points,
                            s.image_metadata = $image_metadata
                ON CREATE SET s.name = $name, s.text = $text, s.bullet_points = $bullet_points,
                            s.image_metadata = $image_metadata
                MERGE (s)-[r:SUBTOPIC_OF]->(t)
                ON MATCH SET r.position = $position
                ON CREATE SET r.position = $position
                """,
                {
                    "topic_id": parent_topic_id,
                    "subtopic_id": subtopic.id,
                    "name": subtopic.name,
                    "text": subtopic.full_text,
                    "bullet_points": subtopic.bullet_points,
                    "image_metadata": image_metadata_json,
                    "position": position
                }
            )
            return True
        except Exception as e:
            print(f"Error creating and linking subtopic {subtopic.id} to topic {parent_topic_id}: {e}")
            return False

    def query_db(self, user_query: str) -> Dict[str, Any]:
        """
        Query the database using LangChain's KuzuQAChain.

        :param user_query: Natural language query (e.g., "What topics have bullet points about X?").
        :return: Response dictionary from the QA chain.
        """
        try:
            response = self.qa_chain.invoke(user_query)
            return response
        except Exception as e:
            print(f"Error querying database: {e}")
            return {"error": str(e)}

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        """
        Retrieve a topic by ID and return it as a Topic object.

        :param topic_id: ID of the topic to retrieve.
        :return: Topic object or None if not found.
        """
        try:
            response = self.conn.execute(
                "MATCH (t:Topic {id: $id}) RETURN t",
                {"id": topic_id}
            )
            if response.has_next():
                data = response.get_next()[0]  # Assuming 't' is a dict
                return Topic(
                    id=data["id"],
                    name=data["name"]
                )
            return None
        except Exception as e:
            print(f"Error retrieving topic {topic_id}: {e}")
            return None

    def get_subtopics(self, topic_id: str) -> List[Subtopic]:
        """
        Retrieve all subtopics of a topic as Subtopic objects.
        
        :param topic_id: ID of the parent topic.
        :return: List of Subtopic objects.
        """
        try:
            response = self.conn.execute(
                """
                MATCH (s:Subtopic)-[r:SUBTOPIC_OF]->(t:Topic {id: $id})
                RETURN s, r.position ORDER BY r.position
                """,
                {"id": topic_id}
            )
            subtopics = []
            while response.has_next():
                data = response.get_next()  # Returns (s, position)
                subtopic_data, position = data  # Extracting node and position
                subtopics.append(Subtopic(
                    id=subtopic_data["id"],
                    name=subtopic_data["name"],
                    full_text=subtopic_data["text"],
                    bullet_points=subtopic_data["bullet_points"],
                    image_metadata=json.loads(subtopic_data["image_metadata"])
                ))
            return subtopics
        except Exception as e:
            print(f"Error retrieving subtopics for topic {topic_id}: {e}")
            return []
        
    def create_nested_subtopic(self, parent_id: str, subtopic: Subtopic, position: int = 0, 
                            parent_type: str = "Topic") -> bool:
        """
        Create a subtopic and link it to a parent (which can be either a Topic or another Subtopic).
        This enables creating a hierarchical tree of topics and nested subtopics.

        :param parent_id: ID of the parent (either Topic or Subtopic)
        :param subtopic: Subtopic object to create and link
        :param position: Order of the subtopic within its parent (default 0)
        :param parent_type: Type of the parent node ("Topic" or "Subtopic", default "Topic")
        :return: True if successful, False otherwise
        """
        try:
            # First, ensure we have the SUBTOPIC_OF_SUBTOPIC relationship table
            try:
                self.conn.execute("""
                    CREATE REL TABLE IF NOT EXISTS SUBTOPIC_OF_SUBTOPIC(
                        FROM Subtopic TO Subtopic,
                        position UINT32
                    );
                """)
            except Exception as e:
                print(f"Error creating SUBTOPIC_OF_SUBTOPIC relationship table: {e}")
                return False
                
            # Prepare the subtopic data
            image_metadata_json = json.dumps(subtopic.image_metadata)
            
            # Create the subtopic node regardless of parent type
            self.conn.execute(
                """
                MERGE (s:Subtopic {id: $subtopic_id})
                ON MATCH SET s.name = $name, s.text = $text, s.bullet_points = $bullet_points,
                            s.image_metadata = $image_metadata
                ON CREATE SET s.name = $name, s.text = $text, s.bullet_points = $bullet_points,
                            s.image_metadata = $image_metadata
                """,
                {
                    "subtopic_id": subtopic.id,
                    "name": subtopic.name,
                    "text": subtopic.full_text,
                    "bullet_points": subtopic.bullet_points,
                    "image_metadata": image_metadata_json
                }
            )
            
            # Connect the subtopic to its parent based on parent type
            if parent_type == "Topic":
                self.conn.execute(
                    """
                    MATCH (s:Subtopic {id: $subtopic_id})
                    MATCH (t:Topic {id: $parent_id})
                    MERGE (s)-[r:SUBTOPIC_OF]->(t)
                    ON MATCH SET r.position = $position
                    ON CREATE SET r.position = $position
                    """,
                    {
                        "subtopic_id": subtopic.id,
                        "parent_id": parent_id,
                        "position": position
                    }
                )
            else:  # parent_type == "Subtopic"
                self.conn.execute(
                    """
                    MATCH (s:Subtopic {id: $subtopic_id})
                    MATCH (p:Subtopic {id: $parent_id})
                    MERGE (s)-[r:SUBTOPIC_OF_SUBTOPIC]->(p)
                    ON MATCH SET r.position = $position
                    ON CREATE SET r.position = $position
                    """,
                    {
                        "subtopic_id": subtopic.id,
                        "parent_id": parent_id,
                        "position": position
                    }
                )
                
            return True
        except Exception as e:
            print(f"Error creating nested subtopic {subtopic.id} under {parent_type} {parent_id}: {e}")
            return False

# Example Usage
if __name__ == "__main__":
    db_manager = KuzuDBManager(db_path="./test_db", in_memory=False)
    
    # Create a topic
    topic = Topic(
        id="t1",
        name="Introduction"
    )
    db_manager.create_topic(topic)
    
    # Create and link a subtopic
    subtopic = Subtopic(
        id="s1",
        name="Section 1.1",
        full_text="Subtopic text",
        bullet_points=["- Subpoint 1"],
        image_metadata=[{
            "image_path": "/path/to/subimg1.png",
            "image_name": "sub_diagram",
            "page_number": "1",
            "url": "/images/pdf_name/sub_diagram.png"
        }]
    )
    db_manager.create_and_link_subtopic("t1", subtopic, position=1)
    
    # Query the database
    response = db_manager.query_db("What topics have bullet points about 'Point 1'?")
    print("Query Response:", response)
    
    # Retrieve and print
    retrieved_topic = db_manager.get_topic("t1")
    print("Retrieved Topic:", retrieved_topic)
    subtopics = db_manager.get_subtopics("t1")
    print("Subtopics:", subtopics)