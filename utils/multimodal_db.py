import os
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.rerankers import RRFReranker
from typing import Optional, List
from dotenv import load_dotenv
# Load environment variables from .env file if it exists
load_dotenv()


# Load environment variables with defaults
DB_URI = os.getenv("LANCEDB_URI", "./lancedb")
TABLE_NAME = os.getenv("LANCEDB_TABLE", "multimodal_table")
EMBEDDER_MODEL = os.getenv("EMBEDDER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")



class MultimodalDB:
    def __init__(self, uri=DB_URI, table_name=TABLE_NAME, embedder_model=EMBEDDER_MODEL):
        # Connect to DB
        self.db = lancedb.connect(uri)
        self.embedder = get_registry().get("gemini-text").create()
        self.Schema = self.get_schema(self.embedder)

        # Create or load table
        if table_name in self.db.table_names():
            self.table = self.db.open_table(table_name)

        else:
            self.table = self.db.create_table(table_name, schema=self.Schema, mode="overwrite")

        # Create FTS index unconditionally. 'replace=True' handles existing indices.
        self.table.create_fts_index("text", replace=True)
    # Schema Definition
    def get_schema(self,embedder):
        class Schema(LanceModel):
            text: Optional[str] = embedder.SourceField()
            vector: Vector(embedder.ndims()) = embedder.VectorField()
            image_path: Optional[str]
            file_path: Optional[str]
        return Schema
    def add_entries(self, entries: List[dict]):
        """Add multiple entries with text, optional image/file paths."""

        self.table.add(entries)

    def delete_entry(self, condition: str):
        """Delete rows matching a condition (e.g., 'id = 1' or 'text = \"hello\"')."""
        self.table.delete(condition)

    def update_entries(self, where: str, values: dict = None, values_sql: dict = None):
        """Update rows based on condition."""
        self.table.update(where=where, values=values, values_sql=values_sql)

    def drop_table(self):
        """Drop the current table."""
        self.db.drop_table(TABLE_NAME)

    def hybrid_search_with_rerank(self, query: str, top_k: int = 10):
        """Hybrid search using RRFReranker."""
        reranker = RRFReranker()
        result = (
            self.table.search(query, query_type="hybrid")
            .rerank(reranker=reranker)
            .limit(top_k)
            .to_list()
        )
        return result


def main():
    # Initialize DB
    db = MultimodalDB()

    # Sample data
    data = [
        {"text": "hello world"},
        {"text": "goodbye world"},
        {"text": "another text entry", "image_path": "/images/img1.jpg"}
    ]

    print("\n✅ Adding entries...")
    db.add_entries(data)

    print("\n🔍 Hybrid search with RRFReranker:")
    results = db.hybrid_search_with_rerank("hello", top_k=5)
    for idx, r in enumerate(results, start=1):
        # Print only text and optional metadata, ignore vector
        print(f"{idx}. text: {r.get('text')}, image_path: {r.get('image_path')}")

    print("\n✏️ Updating entries where text = 'goodbye world'...")
    db.update_entries(where="text = 'goodbye world'", values={"text": "farewell world"})

    print("\n🗑️ Deleting entries where text = 'farewell world'...")
    db.delete_entry("text = 'farewell world'")

    print("\n✅ Final search after updates:")
    final_results = db.hybrid_search_with_rerank("hello")
    for idx, r in enumerate(final_results, start=1):
        print(f"{idx}. text: {r.get('text')}, image_path: {r.get('image_path')}")


if __name__ == "__main__":
    main()