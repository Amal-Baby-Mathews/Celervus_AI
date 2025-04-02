# Celervus

## Overview
Celervus is a local standalone tool designed to process PDF books or documentation, dividing them into topics and subtopics. It generates compressed content like bullet points and flashcards using the Groq free model, extracts images, and stores everything in a Kuza DB graph database with vectorized indices for efficient search. Ideal for educational purposes, it maintains a lightweight, local setup.

## Features
- Extracts topics hierarchically from PDF outlines.
- Generates bullet points and flashcards with Groq's free LLM.
- Stores content and image paths in Kuza DB with embeddings for search.
- Links images to topics/subtopics via graph relationships.
## Kuzu Explorer:
docker run -p 8000:8000            -v /home/seq_amal/work_temp/Celervus_temp/Celervus_AI/kuzu_db:/database  -e MODE=READ_ONLY             --rm kuzudb/explorer:latest
[06:43:06.386] INFO (1): Access mode: READ_ONLY
[06:43:06.483] INFO (1): Version of Kuzu: 0.8.2
[06:43:06.483] INFO (1): Storage version of Kuzu: 36
[06:43:06.485] INFO (1): Deployed server started on port: 8000

### Cypher query:
   MATCH (t:Topic)<-[r:SUBTOPIC_OF]-(s:Subtopic)
   RETURN t, s, r
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

## To Do:
- Improve the summarization logic to generate more concise and accurate summaries.
- Enable Groq to create detailed and context-aware bullet points.
- Enhance the algorithm for generating subtopic names to ensure they are more descriptive and relevant.
- Increase the content size provided to the LLM for creating bullet points to improve its performance and contextual understanding.
- Optimize the integration with Groq for better handling of large documents.
- Add support for customizing the level of detail in the generated summaries and flashcards.
- Implement a fallback mechanism for cases where the LLM fails to generate meaningful output.
- Include error handling and logging for Groq API interactions.
- Test and validate the tool with a variety of PDF documents to ensure robustness.
- Update the documentation with examples and best practices for using the tool effectively.
