from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pdf_extraactor import PDFKnowledgeGraph
from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
from typing import List, Dict, Optional, Any
app = FastAPI()
# Mount static files directory for images
app.mount("/images", StaticFiles(directory="extracted_images"), name="images")
origins = ["http://localhost:5173", "http://127.0.0.1:5173","*"]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.post("/create_graph")
async def create_graph(file: UploadFile = File(...), limit: int = 10):
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    pdf_path = os.path.join(uploads_dir, file.filename)# type: ignore[attr-defined]
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
    
    pdf_name = os.path.basename(file.filename).split(".")[0]# type: ignore[attr-defined]
    output_dir = f"./extracted_images/{pdf_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    kg = PDFKnowledgeGraph(pdf_path=pdf_path, output_dir=output_dir)
    await kg.build_knowledge_graph(max_subtopics=limit)#the subtopic nmber is limited for now TESTING
    
    # Store metadata for each topic created (assuming build_knowledge_graph populates topics)
    topics = kg.get_all_topics()
    
    return {"message": "Graph created successfully", "topics": topics}

@app.get("/topics")
def get_all_topics():
    kg = PDFKnowledgeGraph(pdf_path="", output_dir="")
    return kg.get_all_topics()

@app.get("/topics/{topic_id}")
def get_topic_details(topic_id: str):
    kg = PDFKnowledgeGraph(pdf_path="", output_dir="")
    details = kg.get_topic_details(topic_id)
    if not details:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    return details
@app.get("/subtopics/{subtopic_id}")
def get_subtopic_details(subtopic_id: str):
    # Find the topic_id associated with this subtopic_id
    kg = PDFKnowledgeGraph(pdf_path="", output_dir="")
    details = kg.get_subtopic_details(subtopic_id)
    if details:
        return details
    return {"error": f"Subtopic {subtopic_id} not found"}, 404
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