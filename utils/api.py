from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from pydantic import BaseModel, Field
from pdf_extraactor import PDFKnowledgeGraph
from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
from typing import List, Dict, Optional, Any
from fastapi.responses import StreamingResponse
from celerbud import BAMLFunctions  # Assuming BAMLFunctions is your Celerbud class
from kuzu_init import KuzuDBManager  # Assuming KuzuDBManager is your database manager class
from multimodal_db import MultimodalDB  # Assuming MultimodalDB is your LanceDB manager class
import logging
logger= logging.getLogger("uvicorn.error")
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
# Shared DB instance
shared_multimodal_db = MultimodalDB()

# ---- Pydantic Models ----
class Entry(BaseModel):
    text: str
    image_path: Optional[str] = None
    file_path: Optional[str] = None


class UpdateRequest(BaseModel):
    where: str = Field(..., description="Condition for update (e.g., text = 'hello')")
    values: Optional[Dict[str, Any]] = None
    values_sql: Optional[Dict[str, str]] = None


class DeleteRequest(BaseModel):
    condition: str = Field(..., description="Condition for deletion (e.g., text = 'hello')")


# ---- API Endpoints ----

@app.post("/db/add")
def add_entries(entries: List[Entry]):
    """Add multiple entries to LanceDB."""
    try:
        shared_multimodal_db.add_entries([entry.dict() for entry in entries])
        return {"status": "success", "message": f"{len(entries)} entries added"}
    except Exception as e:
        logger.exception(f"Failed to add entries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add entries: {str(e)}")


@app.post("/db/update")
def update_entries(update_req: UpdateRequest):
    """Update entries based on condition."""
    try:
        shared_multimodal_db.update_entries(
            where=update_req.where,
            values=update_req.values,
            values_sql=update_req.values_sql,
        )
        return {"status": "success", "message": f"Entries updated where {update_req.where}"}
    except Exception as e:
        logger.exception(f"Update endpoint failed for where='{update_req.where}': {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


@app.delete("/db/delete")
def delete_entry(delete_req: DeleteRequest):
    """Delete entries from LanceDB based on condition."""
    try:
        shared_multimodal_db.delete_entry(delete_req.condition)
        return {"status": "success", "message": f"Entries deleted where {delete_req.condition}"}
    except Exception as e:
        logger.exception(f"Delete endpoint failed for condition='{delete_req.condition}': {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@app.get("/db/search")
def hybrid_search(query: str, top_k: int = 10):
    """Perform hybrid search with RRFReranker."""
    try:
        results = shared_multimodal_db.hybrid_search_with_rerank(query, top_k)
        cleaned_results = [
            {k: v for k, v in r.items() if k != "vector"} for r in results
        ]
        return {
            "status": "success",
            "query": query,
            "count": len(cleaned_results),
            "results": cleaned_results,
        }
    except Exception as e:
        logger.exception(f"Search endpoint failed for query='{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.delete("/db/drop")
def drop_table():
    """Drop the LanceDB table."""
    try:
        shared_multimodal_db.drop_table()
        return {"status": "success", "message": "Table dropped successfully"}
    except Exception as e:
        logger.exception(f"Drop table failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to drop table: {str(e)}")
# Example Usage
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)