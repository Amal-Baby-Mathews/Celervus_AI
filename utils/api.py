import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pdf_extraactor import PDFKnowledgeGraph
from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
from typing import List, Dict, Optional, Any
from fastapi.responses import StreamingResponse
from celerbud import BAMLFunctions  # Assuming BAMLFunctions is your Celerbud class
from kuzu_init import KuzuDBManager  # Assuming KuzuDBManager is your database manager class
from json_processing import JSONKnowledgeGraph  # Assuming JSONKnowledgeGraph is your JSON processing class
from fastapi import Body

app = FastAPI()

# Mount static files directory for images
app.mount("/images", StaticFiles(directory="extracted_images"), name="images")

origins = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Shared KuzuDBManager instance for all operations
shared_db_manager = KuzuDBManager(db_path="./kuzu_db", in_memory=False)
print(f"Initialized shared KuzuDBManager with db_path: {shared_db_manager.db_path}")
@app.post("/create_graph")
async def create_graph(file: UploadFile = File(...), limit: int = 10):
    """Create a knowledge graph from an uploaded PDF file.

    Args:
        file (UploadFile): The PDF file to process.
        limit (int): Maximum number of subtopics to extract (default: 10).

    Returns:
        dict: Success message and list of topics created.
    """
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    pdf_path = os.path.join(uploads_dir, file.filename)  # type: ignore[attr-defined]
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    
    pdf_name = os.path.basename(file.filename).split(".")[0]  # type: ignore[attr-defined]
    output_dir = f"./extracted_images/{pdf_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    kg = PDFKnowledgeGraph(pdf_path=pdf_path, output_dir=output_dir, db_manager=shared_db_manager)
    await kg.build_knowledge_graph(max_subtopics=limit)  # Subtopic number limited for testing
    
    # Store metadata for each topic created
    topics = kg.get_all_topics()
    
    return {"message": "Graph created successfully", "topics": topics}

    # Test with curl:
    # curl -X POST "http://localhost:8008/create_graph?limit=5" -F "file=@/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/Applied-Machine-Learning-and-AI-for-Engineers.pdf"

@app.get("/topics")
def get_all_topics():
    """Retrieve all topics in the knowledge graph.

    Returns:
        list: List of all topics.
    """
    kg = PDFKnowledgeGraph(pdf_path="", output_dir="", db_manager=shared_db_manager)  # Note: This might need a valid path in practice
    return kg.get_all_topics()

    # Test with curl:
    # curl -X GET "http://localhost:8008/topics"

@app.get("/topics/{topic_id}")
def get_topic_details(topic_id: str):
    """Retrieve details of a specific topic by ID.

    Args:
        topic_id (str): The ID of the topic to retrieve.

    Returns:
        dict: Topic details or 404 if not found.
    """
    kg = PDFKnowledgeGraph(pdf_path="", output_dir="", db_manager=shared_db_manager)  # Note: This might need a valid path in practice
    details = kg.get_topic_details(topic_id)
    if not details:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    return details

    # Test with curl:
    # curl -X GET "http://localhost:8008/topics/ff0e7064-dcc9-4b00-a712-28b703574ba4"

@app.get("/subtopics/{subtopic_id}")
def get_subtopic_details(subtopic_id: str):
    """Retrieve details of a specific subtopic by ID.

    Args:
        subtopic_id (str): The ID of the subtopic to retrieve.

    Returns:
        dict: Subtopic details or error message if not found.
    """
    kg = PDFKnowledgeGraph(pdf_path="", output_dir="", db_manager=shared_db_manager)  # Note: This might need a valid path in practice
    details = kg.get_subtopic_details(subtopic_id)
    if details:
        return details
    return {"error": f"Subtopic {subtopic_id} not found"}, 404

    # Test with curl:
    # curl -X GET "http://localhost:8008/subtopics/s1"

@app.get("/query")
def query_endpoint(query: str):
    """FastAPI endpoint to stream graph query results.

    Args:
        query (str): The natural language query to process.

    Returns:
        StreamingResponse: Streams the query processing results in real-time.
    """
    celerbud = BAMLFunctions(kuzu_client=shared_db_manager)
    return StreamingResponse(
        celerbud.query_graph(query),  # Assuming query_graph_stream is defined in BAMLFunctions
        media_type="text/plain"
    )

    # Test with curl (use -N for no buffering to see streaming):
    # curl -N -X GET "http://localhost:8008/query?query=What%20subtopics%20are%20under%20the%20topic%20'Barcode%20Scanning%20Procedure:%20Align%20and%20Capture%20Barcode%20Data'?"
# New endpoint to ingest a JSON file
@app.post("/ingest_json_file")
async def ingest_json_file(file: UploadFile = File(...), node_table: str = "Node", rel_table: Optional[str] = None):
    """Ingest a JSON file into the KuzuDB knowledge graph.

    Args:
        file (UploadFile): The JSON file to ingest.
        node_table (str): Name of the node table (default: 'Node').
        rel_table (Optional[str]): Name of the relationship table (if applicable).

    Returns:
        dict: Success message or error.
    """
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    json_path = os.path.join(uploads_dir, file.filename) # type: ignore
    with open(json_path, "wb") as f:
        f.write(await file.read())

    try:
        jkg = JSONKnowledgeGraph(db_manager=shared_db_manager)
        jkg.ingest_json_file(json_path, node_table=node_table, rel_table=rel_table)
        return {"message": f"Successfully ingested JSON file '{file.filename}' into table(s)."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error ingesting JSON file: {str(e)}")

    # Test with curl:
    # curl -X POST "http://localhost:8008/ingest_json_file?node_table=Person" -F "file=@/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/people.json"

# New endpoint to ingest a JSON string
@app.post("/ingest_json_string")
async def ingest_json_string(json_data: Any = Body(...), node_table: str = "Node", rel_table: Optional[str] = None):
    """Ingest a JSON string into the KuzuDB knowledge graph.

    Args:
        json_data (Any): The JSON data (array, object, or string) to ingest.
        node_table (str): Name of the node table (default: 'Node').
        rel_table (Optional[str]): Name of the relationship table (if applicable).

    Returns:
        dict: Success message or error.
    """
    try:
        # Convert the input to a JSON string, regardless of its initial type
        if isinstance(json_data, str):
            # If it’s already a string, validate it’s proper JSON
            json.loads(json_data)
            json_str = json_data
        else:
            # If it’s an object/array, stringify it
            json_str = json.dumps(json_data)

        jkg = JSONKnowledgeGraph(db_manager=shared_db_manager)
        jkg.ingest_json_string(json_str, node_table=node_table, rel_table=rel_table)
        return {"message": "Successfully ingested JSON string into table(s)."}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error ingesting JSON string: {str(e)}")

    # Test with curl:
    # curl -X POST "http://localhost:8008/ingest_json_string?node_table=Person" -H "Content-Type: application/json" -d '[{"id": "p1", "name": "Gregory"}]'
@app.get("/json_nodes")
def get_json_nodes(json_only: bool = True):
    """Retrieve all JSON-ingested node tables with their IDs in the knowledge graph.

    Args:
        json_only (bool): If True, only return JSON-ingested tables (default: True).

    Returns:
        List[Dict[str, Any]]: List of node tables with 'id' and 'name'.
    """
    jkg = JSONKnowledgeGraph(db_manager=shared_db_manager)
    nodes = jkg.list_json_nodes(json_only=json_only)
    return nodes
@app.get("/json_nodes_by_id/{table_id}")
async def get_json_table_nodes_by_id(table_id: int, id: Optional[str] = None, name: Optional[str] = None):
    """Retrieve nodes from a specific JSON-ingested table by table ID.

    Args:
        table_id (int): The ID of the JSON-ingested table (e.g., 3 for 'JSON_Person').
        id (Optional[str]): Filter by node ID (exact match).
        name (Optional[str]): Filter by node name (exact match).

    Returns:
        List[Dict[str, Any]]: List of nodes matching the criteria.

    Raises:
        HTTPException: If the table ID does not exist or an error occurs.
    """
    try:
        jkg = JSONKnowledgeGraph(db_manager=shared_db_manager)
        nodes = jkg.get_json_table_nodes(table_id, id=id, name=name)
        return nodes
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving nodes: {str(e)}")

    # Test with curl:
    # curl -X GET "http://localhost:8008/json_nodes_by_id/3"
    # curl -X GET "http://localhost:8008/json_nodes_by_id/3?id=p1"
    # curl -X GET "http://localhost:8008/json_nodes_by_id/3?name=Gregory"
# In main.py
@app.get("/query_json/{table_id}")
async def query_json_table(table_id: int, query: str):
    """Query a specific JSON-ingested table using NLP.

    Args:
        table_id (int): The ID of the JSON-ingested table to query.
        query (str): The natural language query.

    Returns:
        dict: Response with the natural language answer.
    """
    try:
        jkg = JSONKnowledgeGraph(db_manager=shared_db_manager)
        answer = jkg.query_graph_nlp(query, table_id)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying table ID {table_id}: {str(e)}")

    # Test with curl:
    # curl -X GET "http://localhost:8008/query_json/3?query=What%20is%20the%20name%20of%20the%20person%20with%20ID%20'p1'?"
# Example Usage
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)