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

# Example Usage
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)