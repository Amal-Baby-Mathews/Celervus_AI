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
## LLM Integration

To make the tool flexible and allow the use of different LLM sources (e.g., Groq, OpenRouter, etc.), you can implement a modular approach for LLM integration. Below is an outline of how to achieve this:

### Steps to Integrate Multiple LLM Sources

1. **Abstract LLM Interaction**:
   Create a Python module (e.g., `llm_handler.py`) that defines a common interface for interacting with different LLMs. For example:
   ```python
   class LLMHandler:
       def __init__(self, llm_type, api_key):
           self.llm_type = llm_type
           self.api_key = api_key

       def generate_summary(self, text):
           if self.llm_type == "groq":
               return self._use_groq(text)
           elif self.llm_type == "openrouter":
               return self._use_openrouter(text)
           else:
               raise ValueError("Unsupported LLM type")

       def _use_groq(self, text):
           # Add Groq-specific API call logic here
           pass

       def _use_openrouter(self, text):
           # Add OpenRouter-specific API call logic here
           pass
   ```

2. **Environment Configuration**:
   Allow users to specify the LLM source and API key via environment variables:
   ```bash
   export LLM_TYPE='groq'  # or 'openrouter'
   export LLM_API_KEY='your-api-key'
   ```

3. **Dynamic LLM Selection**:
   Update the main script to dynamically select the LLM source based on the environment variables:
   ```python
   import os
   from llm_handler import LLMHandler

   llm_type = os.getenv("LLM_TYPE", "groq")
   api_key = os.getenv("LLM_API_KEY")

   llm_handler = LLMHandler(llm_type, api_key)

   # Example usage
   summary = llm_handler.generate_summary("Your input text here")
   print(summary)
   ```

4. **Extend Support for New LLMs**:
   Add new methods in `LLMHandler` for additional LLM sources as needed.

### Benefits
- **Flexibility**: Easily switch between LLMs without modifying the core logic.
- **Scalability**: Add support for new LLMs with minimal changes.
- **User-Friendly**: Configure LLM preferences via environment variables.

### To Do
- Implement and test the `LLMHandler` class with Groq and OpenRouter.
- Add error handling for API failures and invalid configurations.
- Document the setup process for each supported LLM.

