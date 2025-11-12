# Celervus System Architecture

## Overview

Celervus is a local standalone application designed to process PDF documents, extract knowledge, and provide efficient search capabilities. The system implements a multimodal approach combining text and image processing with both graph and vector databases for optimal retrieval performance.

## System Architecture

### Core Components

#### 1. FastAPI Backend (api.py)
The FastAPI backend serves as the central hub of the application, providing RESTful API endpoints for all system operations.

**Key Responsibilities:**
- Handles HTTP requests and responses
- Manages file uploads and downloads
- Provides CORS support for frontend integration
- Orchestrates interactions between different databases
- Serves static image files

**Key Endpoints:**
- `/create_graph` - Create knowledge graph from uploaded PDF
- `/topics` - Retrieve topics from graph database
- `/subtopics/{subtopic_id}` - Get details of specific subtopic
- `/query` - Query graph database with natural language
- `/db/add` - Add entries to multimodal database
- `/db/search` - Perform hybrid search
- `/db/image_search_by_pk` - Perform image-to-image search
- `/db/update`, `/db/delete`, `/db/drop` - Database management

#### 2. Knowledge Graph Database (Kuzu DB)
The Kuzu graph database stores hierarchical topic relationships extracted from PDF documents.

**Key Features:**
- Stores topics as nodes with `Topic` label
- Stores subtopics as nodes with `Subtopic` label
- Relationships between topics and subtopics via `SUBTOPIC_OF` edge
- Supports Cypher queries for complex relationship traversal
- Hierarchical structure representing document outline

**Structure:**
```
(Topic) --[SUBTOPIC_OF]--> (Subtopic)
```

#### 3. Multimodal Database (LanceDB)
The LanceDB instance provides vector storage and similarity search capabilities for both text and images.

**Key Features:**
- Hybrid search combining full-text and vector search
- Image-to-image similarity search using vector embeddings
- Support for both text and image embeddings in the same table
- RRFReranker for improved search result ranking
- Automatic embedding computation for new entries

**Schema:**
- `pk`: Primary key (UUID)
- `text`: Text content for the entry
- `text_vector`: Vector embedding for text content
- `image_path`: Path to associated image
- `image_vector`: Vector embedding for image content
- `file_path`: Original file path

#### 4. PDF Processing Module (pdf_extraactor.py)
Handles the extraction of text, images, and hierarchical structure from PDF documents.

**Key Features:**
- Extracts topics and subtopics from PDF outlines
- Extracts images from PDF pages
- Generates summaries and flashcards using LLMs
- Creates knowledge graph relationships
- Uses PyMuPDF, spaCy, and embeddings for subtopic extraction

#### 5. Embedding System (DINO Model)
The system uses the DINO (DEep Image Embeddings) model for image embeddings and various text embedders for text content.

**DINO Embedding (DINOv3Embedding class):**
- Uses `facebook/dinov2-base-imagenet1k-1-layer` as default model
- Implements Hugging Face Transformers
- Computes feature vectors from image pixels
- Provides 768-dimensional embeddings
- Handles image preprocessing and embedding computation

**Text Embeddings:**
- Supports multiple embedders (HuggingFace, Ollama)
- Default: `nomic-embed-text:latest` via Ollama
- Configurable through environment variables

### Data Flow

#### PDF Processing Flow:
1. User uploads PDF via `/create_graph` endpoint
2. PDF is saved to `uploads/` directory
3. PDFKnowledgeGraph processes the document:
   - Extracts topic hierarchy
   - Extracts images from pages
   - Generates summaries using LLM
4. Creates nodes and relationships in Kuzu DB
5. Extracted images are saved to `extracted_images/{pdf_name}/`

#### Search Flow:
1. **Text Search (Hybrid)**:
   - Query hits `/db/search` endpoint
   - Uses both full-text search and vector search
   - Results are reranked using RRFReranker
   - Returns relevant text and image content

2. **Image Search**:
   - Query hits `/db/image_search_by_pk` endpoint
   - Retrieves original image embedding
   - Performs vector similarity search
   - Returns similar images with associated text

3. **Knowledge Graph Query**:
   - Natural language query hits `/query` endpoint
   - BAMLFunctions processes the query
   - Translates to Cypher query
   - Returns graph traversal results

### Configuration and Environment Variables

The system supports various configuration options through environment variables:

- `LANCEDB_URI`: Path to LanceDB directory (default: "./lancedb")
- `LANCEDB_TABLE`: Name of the table (default: "multimodal_table")
- `EMBEDDING_PROVIDER`: Text embedder provider (default: "ollama")
- `EMBEDDER_MODEL`: Text embedder model (default: "nomic-embed-text:latest")
- `IMAGE_EMBEDDER_MODEL`: Image embedder model (default: "facebook/dinov2-base-imagenet1k-1-layer")
- `HF_TOKEN`: Hugging Face token for private models
- `IMAGES_DIR`: Directory for storing images (default: "./datasets/open_images_sample")
- `BASE_URL`: Base URL for image serving

### Directory Structure

```
.
├── README.md
├── requirements.txt
├── Applied-Machine-Learning-and-AI-for-Engineers.pdf
├── Heart.pdf
├── Kuzu_Vector.md
├── utils/
│   ├── api.py                 # FastAPI backend
│   ├── multimodal_db.py       # LanceDB integration
│   ├── pdf_extraactor.py      # PDF processing
│   ├── kuzu_init.py           # Kuzu DB initialization
│   ├── kuzu_explorer.py       # Kuzu DB exploration
│   ├── celerbud.py            # BAML functions
│   ├── diagnosed.py           # Error diagnosis
│   ├── sample_ingester.py     # Data ingestion
│   ├── datasets/              # Dataset storage
│   ├── extracted_images/      # PDF-extracted images
│   ├── uploads/               # Uploaded PDFs
│   └── lancedb/              # LanceDB files (if not default)
├── my-knowledge-graph-app/   # Frontend application
└── celervusenv/              # Python virtual environment
```

### Technology Stack

**Backend:**
- Python 3.12
- FastAPI for web framework
- Pydantic for data validation
- Uvicorn for ASGI server

**Databases:**
- Kuzu DB for graph storage
- LanceDB for vector storage

**ML & AI:**
- Hugging Face Transformers for DINO embeddings
- PyTorch for model execution
- Ollama for text embeddings (default)
- spaCy for NLP processing

**PDF Processing:**
- PyMuPDF (fitz) for PDF operations
- PIL for image handling

**Frontend (Separate):**
- React with Vite
- Tailwind CSS
- TypeScript
- Material UI components

### Security Considerations

- Input validation on all endpoints
- File type validation for uploads
- Sanitized file paths to prevent directory traversal
- Environment variables for sensitive data
- CORS configured for specific origins

### Scalability Considerations

- Modular architecture allows independent scaling of components
- Separate databases for different access patterns
- Vector search in LanceDB for efficient similarity queries
- Graph database for relationship queries
- Asynchronous processing where applicable

## Deployment

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Set up Ollama and pull required models
3. Configure environment variables
4. Run the API: `cd utils && python api.py`
5. Access API at `http://localhost:8008`

### Production Considerations
- Use proper web server (e.g., nginx) in front of Uvicorn
- Configure proper logging and monitoring
- Database backup strategies for both Kuzu and LanceDB
- Image storage management and cleanup
- Rate limiting and request validation