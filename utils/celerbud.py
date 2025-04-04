from typing import List, Optional
from baml_client import b
from baml_client.types import ChatMessage, ContextSource, ChatResponse, BulletPoints
import os
from dotenv import load_dotenv

# Load API keys from .env if available
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class BAMLFunctions:
    def __init__(self):
        self.client = b

    def streaming_chat(self, messages: List[ChatMessage]) -> ChatResponse:
        """Fetches the best context for the query and executes a streaming chat function."""
        user_message = next((msg for msg in messages if msg.role == "user"), None)
        context = self.get_best_context(user_message.content) if user_message else []
        return self.client.StreamingChat(messages=messages, context=context)

    def extract_bullet_points(self, text: str) -> BulletPoints:
        """Extracts bullet points from a given text."""
        return self.client.ExtractBulletPoints(text=text)

    # Dummy function to fetch context from vector database
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
