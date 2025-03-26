# Celervus

## Overview
Celervus is a local standalone tool designed to process PDF books or documentation, dividing them into topics and subtopics. It generates compressed content like bullet points and flashcards using the Groq free model, extracts images, and stores everything in a Kuza DB graph database with vectorized indices for efficient search. Ideal for educational purposes, it maintains a lightweight, local setup.

## Features
- Extracts topics hierarchically from PDF outlines.
- Generates bullet points and flashcards with Groq's free LLM.
- Stores content and image paths in Kuza DB with embeddings for search.
- Links images to topics/subtopics via graph relationships.

## Setup
1. **Install Dependencies**:
   ```bash
   pip install PyPDF2 kuzu ollama groq pillow    
   ```
2. **Set Up Groq API Key**:
   - Get a free API key from [Groq](https://console.groq.com/docs).
   - Export it:
     ```bash
     export GROQ_API_KEY='your-groq-api-key'
     ```
3. **Set Up Ollama**:
   - Install Ollama and pull the `nomic-embed-text` model:
     ```bash
     ollama pull nomic-embed-text
     ```
4. **Prepare Your PDF**:
   - Place your PDF in the project directory.

## Code
[To be added: Main script details and snippets]

## Usage
[To be added: Step-by-step instructions for running the tool]

## License
MIT License - feel free to use, modify, and distribute.

## Contributing
Contributions welcome! Fork the repo, make changes, and submit a pull request.
