import asyncio
from typing import List, Optional
from baml_client import b
from baml_client.types import ChatMessage, ContextSource, ChatResponse, BulletPoints,GraphResult,GraphSchema
import os
from dotenv import load_dotenv
from kuzu_init import KuzuDBManager
import re
# Load API keys from .env if available
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class BAMLFunctions:
    def __init__(self):
        self.client = b                    
        self.kuzu_client= KuzuDBManager()
    def streaming_chat(self, messages: List[ChatMessage]) -> ChatResponse:
        """Fetches the best context for the query and executes a streaming chat function."""
        user_message = next((msg for msg in messages if msg.role == "user"), None)
        context = self.get_best_context(user_message.content) if user_message else []
        return self.client.StreamingChat(messages=messages, context=context)

    def extract_bullet_points(self, text: str) -> BulletPoints:
        """Extracts bullet points from a given text."""
        return self.client.ExtractBulletPoints(text=text)
    def generate_response(self, messages: List[ChatMessage]) -> ChatResponse:
        """Generates a response based on the provided messages."""  
        user_message = next((msg for msg in messages if msg.role == "user"), None)
        context = self.get_best_context(user_message.content) if user_message else []
        return self.client.GenerateResponse(messages=messages, context=context)
    # Dummy function to fetch context from vector database
    # New methods for the new BAML functions
    def generate_document_title(self, text_chunks: str) -> str:
        """Generates a document title using BAML."""
        return self.client.GenerateDocumentTitle(text_chunks=text_chunks)

    def generate_subtopic_name(self, subtopic_text: str) -> str:
        """Generates a subtopic name using BAML."""
        return self.client.GenerateSubtopicName(subtopic_text=subtopic_text)

    def check_subtopic_relevance(self, text: str) -> float:
        """Checks subtopic relevance using BAML."""
        return self.client.CheckSubtopicRelevance(text=text)
    def fetch_context_from_vector_db(self, query: str) -> List[ContextSource]:
        """Fetches relevant context from a vector database (dummy implementation)."""
        return [
            ContextSource(
                sourceType="vector_db",
                content=f"Relevant vector DB content for query: {query}",
                relevanceScore=0.95,
            )
        ]

    # Dummy function to fetch context from a document retrieval system
    def fetch_context_from_documents(self, query: str) -> List[ContextSource]:
        """Fetches relevant context from document sources (dummy implementation)."""
        return [
            ContextSource(
                sourceType="document",
                content=f"Relevant document content for query: {query}",
                relevanceScore=0.85,
            )
        ]

    # Dummy function to fetch context from an external API
    def fetch_context_from_api(self, query: str) -> List[ContextSource]:
        """Fetches relevant context from an external API (dummy implementation)."""
        return [
            ContextSource(
                sourceType="api",
                content=f"API response with relevant data for query: {query}",
                relevanceScore=0.90,
            )
        ]

    def get_best_context(self, query: str) -> List[ContextSource]:
        """Combines multiple context sources and selects the best ones based on relevance scores."""
        vector_context = self.fetch_context_from_vector_db(query)
        document_context = self.fetch_context_from_documents(query)
        api_context = self.fetch_context_from_api(query)

        # Combine and sort by relevance score
        all_context = vector_context + document_context + api_context
        sorted_context = sorted(all_context, key=lambda c: c.relevanceScore, reverse=True)
        
        return sorted_context[:2]  # Return top 2 most relevant context sources
    def query_graph(self, query: str) -> str:
            """Queries a graph database using BAML and streams the natural language response.

            Args:
                query (str): The natural language question to query the graph database.

            Returns:
                str: The final natural language answer based on the query results.
            """
            try:
                print(f"Starting query_graph with query: {query}")

                # Step 1: Retrieve the schema from KuzuDB
                print("Retrieving schema from KuzuDB...")
                schema_str = self.kuzu_client.get_schema()
                print(f"Schema retrieved as string:\n{schema_str}")

                # Parse the structured string back into GraphSchema
                nodes = []
                relationships = []
                properties = []
                
                # Extract nodes
                node_section = re.search(r"Nodes:\n(.*?)(?:\nRelationships:|$)", schema_str, re.DOTALL)
                if node_section and "None" not in node_section.group(1):
                    for line in node_section.group(1).splitlines():
                        if line.strip().startswith("- "):
                            nodes.append(line.strip()[2:])  # Remove "  - "

                # Extract relationships
                rel_section = re.search(r"Relationships:\n(.*?)(?:\nProperties:|$)", schema_str, re.DOTALL)
                if rel_section and "None" not in rel_section.group(1):
                    for line in rel_section.group(1).splitlines():
                        if line.strip().startswith("- "):
                            relationships.append(line.strip()[2:])

                # Extract properties
                prop_section = re.search(r"Properties:\n(.*)", schema_str, re.DOTALL)
                if prop_section and "None" not in prop_section.group():
                    for line in prop_section.group(1).splitlines():
                        if line.strip().startswith("- "):
                            properties.append(line.strip()[2:])

                schema = GraphSchema(nodes=nodes, relationships=relationships, properties=properties)
                print(f"Parsed schema: Nodes - {schema.nodes}, Relationships - {schema.relationships}, Properties - {schema.properties}")
                
                if not schema.nodes and not schema.relationships:
                    return "Error: No schema found in the database."

                # Step 2: Generate an OpenCypher query using BAML
                print("Generating OpenCypher query using BAML...")
                graph_query = self.client.GenerateGraphQuery(question=query, schema=schema)
                cypher_query = graph_query.query
                print(f"Generated Cypher query: {cypher_query}")
                if not cypher_query:
                    return "Error: Failed to generate a valid Cypher query."

                # Step 3: Execute the query against KuzuDB
                print("Executing Cypher query against KuzuDB...")
                response = self.kuzu_client.conn.execute(cypher_query)
                result_data = []
                while response.has_next():
                    result_data.append(response.get_next())
                print(f"Query execution results: {result_data}")

                # Convert result to a string representation
                result_str = "\n".join([str(row) for row in result_data]) if result_data else "No results found."
                print(f"Formatted query results: {result_str}")
                graph_result = GraphResult(result=result_str)

                # Step 4: Analyze the results using BAML with streaming
                print("Analyzing results using BAML with streaming...")
                stream = self.client.stream.AnalyzeResults(
                    question=query,
                    query=cypher_query,
                    results=graph_result
                )

                # Process stream as it comes in
                for partial in stream:# type: ignore
                    if partial.answer:
                        print(f"Current answer: {partial.answer.value}")
                        print(f"Stream state: {partial.answer.state}")
                    if partial.queryUsed:  # Only appears when complete due to @stream.done
                        print(f"Query: {partial.queryUsed}")
                    if partial.rawResults:  # Only appears when complete due to @stream.done
                        print(f"Results: {partial.rawResults}")

                # Step 5: Get final validated response after stream completes
                final = stream.get_final_response() # type: ignore
                print(f"Final natural language response: {final.answer}")
                return final.answer

            except Exception as e:
                print(f"Error querying graph: {e}")
                return f"Error: Unable to process query '{query}' due to {str(e)}"
if __name__ == "__main__":
    celerbud = BAMLFunctions()  # Assuming proper initialization
    query = "What subtopics are under the topic 'Barcode Scanning Procedure: Align and Capture Barcode Data'?"
    result = celerbud.query_graph(query)
    print(f"Final result: {result}")