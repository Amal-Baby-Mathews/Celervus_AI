# Requirements & Dependencies

This document provides a comprehensive overview of all dependencies and requirements for the Celervus system, including both backend and frontend components.

## Backend Dependencies (Python)

### Core Dependencies
- **Python 3.12** - Runtime environment
- **FastAPI** (0.115.12) - Web framework for building APIs
- **Uvicorn** (0.34.0) - ASGI server for running FastAPI
- **Pydantic** (2.10.6) - Data validation and settings management
- **Pydantic Settings** (2.8.1) - Settings management with Pydantic v2
- **Python-Multipart** (0.0.20) - Multipart data support for file uploads

### Database Dependencies
- **Kuzu** (0.8.2) - Graph database system
- **LanceDB** (via BAML-py 0.82.0) - Vector database for multimodal search

### PDF Processing Dependencies
- **PyMuPDF** (1.25.4) - PDF processing and manipulation
- **PyPDF2** (3.0.1) - PDF extraction capabilities
- **spaCy** (3.8.4) - Advanced natural language processing
- **en_core_web_md** - English language model for spaCy

### AI/ML Dependencies
- **Hugging Face Hub** (0.30.1) - Model hub integration
- **Transformers** (4.50.3) - Transformers library for NLP models
- **Torch/PyTorch** (2.6.0) - Deep learning framework for DINO model
- **Ollama** (0.4.7) - Local LLM execution
- **Groq** (0.20.0) - Cloud-based LLM API
- **Pillow** (11.1.0) - Image processing
- **Langchain** (0.3.20) - LLM application framework
- **Langchain-Groq** (0.2.4) - Groq integration for Langchain
- **Langchain-Ollama** (0.2.3) - Ollama integration for Langchain
- **Langchain-Kuzu** (0.3.0) - Kuzu DB integration for Langchain
- **Sentence-Transformers** (4.0.1) - Pre-trained sentence transformers

### Data Processing Dependencies
- **Pandas** (2.2.3) - Data manipulation and analysis
- **NumPy** (2.2.4) - Numerical computing
- **Requests** (2.32.3) - HTTP library
- **Aiohttp** (3.11.14) - Async HTTP client/server
- **Tqdm** - Progress bars for long-running operations

### Configuration & Utilities
- **Python-Dotenv** (1.1.0) - Environment variable management
- **Typer** (0.15.2) - CLI application framework
- **Dataclasses-Json** (0.6.7) - Dataclass to JSON conversion
- **AnyIO** (4.9.0) - Async IO compatibility layer
- **Sniffio** (1.3.1) - Async library detection

### Additional Dependencies
- **Langcodes** (3.5.0) - Language code handling
- **Weasel** (0.4.1) - Utility functions
- **Thinc** (8.3.4) - Configuration and behavior framework
- **Marisa-Trie** (1.2.1) - Fast and efficient trie data structure
- **Language-Data** (1.3.0) - Language-related data access
- **Setuptools** (78.1.0) - Python package discovery and dependencies
- **Scikit-learn** (1.6.1) - Machine learning tools
- **Scipy** (1.15.2) - Scientific computing tools

## Frontend Dependencies (JavaScript/React)

### Core Dependencies
- **Node.js** - JavaScript runtime environment
- **React** (19.0.0) - Frontend library for building user interfaces
- **React DOM** (19.0.0) - React package for DOM manipulation
- **React Router DOM** (7.4.1) - Declarative routing for React

### UI & Styling Dependencies
- **Tailwind CSS** (4.1.0) - Utility-first CSS framework
- **Tailwind CSS CLI** (4.1.0) - Command line interface for Tailwind
- **@tailwindcss/postcss** (4.1.0) - Tailwind CSS PostCSS plugin
- **Autoprefixer** (10.4.21) - CSS vendor prefixing
- **Lucide React** (0.487.0) - Icon library
- **Framer Motion** (12.6.3) - Production-ready motion library
- **React Icons** (5.5.0) - Popular icon sets

### HTTP Client
- **Axios** (1.8.4) - Promise-based HTTP client for making API requests

### Development Dependencies
- **Vite** (6.2.0) - Fast build tool and development server
- **@vitejs/plugin-react** (4.3.4) - Vite plugin for React projects
- **ESLint** (9.21.0) - JavaScript linter
- **@eslint/js** (9.21.0) - ESLint base configurations
- **eslint-plugin-react-hooks** (5.1.0) - ESLint rules for React Hooks
- **eslint-plugin-react-refresh** (0.4.19) - ESLint plugin for React Fast Refresh
- **@types/react** (19.0.10) - TypeScript definitions for React
- **@types/react-dom** (19.0.4) - TypeScript definitions for React DOM
- **Globals** (15.15.0) - ECMAScript global variables
- **PostCSS** (8.5.3) - CSS processing tool

## System Requirements

### Backend Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2 support
- **Python**: 3.12 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for optimal performance)
- **Storage**: Minimum 2GB free space for dependencies and models
- **Optional GPU Support**: For accelerated model inference with PyTorch

### Frontend Requirements
- **Node.js**: 18.0 or higher
- **npm** or **yarn**: Package managers
- **Browser**: Modern browser with ES6 support (Chrome, Firefox, Safari, Edge)

## External Services & APIs

### Required Services
- **Ollama**: For local text embeddings (requires nomic-embed-text model)
- **Groq API**: For cloud-based LLM processing (requires API key)
- **Hugging Face Hub**: For DINO image embedding model access

### Optional Services
- **Docker**: For Kuzu Explorer visualization
- **GPU**: For accelerated PyTorch operations

## Installation Commands

### Backend Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (if not already installed)
# Follow instructions at: https://ollama.com/download

# Pull required models
ollama pull nomic-embed-text
```

### Frontend Installation
```bash
# Navigate to frontend directory
cd my-knowledge-graph-app

# Install dependencies
npm install
```

## Environment Variables

### Backend Environment Variables
- `GROQ_API_KEY`: API key for Groq cloud service
- `HF_TOKEN`: Hugging Face token for private models
- `LLM_TYPE`: LLM provider ('groq', 'openrouter', etc.)
- `LLM_API_KEY`: API key for selected LLM provider
- `LANCEDB_URI`: Path to LanceDB directory (default: "./lancedb")
- `LANCEDB_TABLE`: Name of the table (default: "multimodal_table")
- `EMBEDDING_PROVIDER`: Text embedder provider (default: "ollama")
- `EMBEDDER_MODEL`: Text embedder model (default: "nomic-embed-text:latest")
- `IMAGE_EMBEDDER_MODEL`: Image embedder model (default: "facebook/dinov2-base-imagenet1k-1-layer")
- `IMAGES_DIR`: Directory for storing images (default: "./datasets/open_images_sample")
- `BASE_URL`: Base URL for image serving (default: "http://localhost:8008")

### Frontend Environment Variables
- No specific environment variables required for the frontend
- API endpoints are configured to connect to `http://localhost:8008` by default