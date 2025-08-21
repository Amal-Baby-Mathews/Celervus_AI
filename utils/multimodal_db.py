import os
import uuid
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.rerankers import RRFReranker
from typing import Optional, List
from dotenv import load_dotenv
from pydantic import Field
from transformers import AutoModel, AutoImageProcessor
# Load environment variables from .env file if it exists
load_dotenv()
from PIL import Image
import torch
# Load environment variables with defaults
DB_URI = os.getenv("LANCEDB_URI", "./lancedb")
TABLE_NAME = os.getenv("LANCEDB_TABLE", "multimodal_table")
EMBEDDER_MODEL = os.getenv("EMBEDDER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
IMAGE_EMBEDDER_MODEL = os.getenv("IMAGE_EMBEDDER_MODEL", "facebook/dinov2-small-imagenet1k-1-layer")
from logging import getLogger
import logging
HF_TOKEN = os.getenv("HF_TOKEN", None)  # Load token from .env, if available
class DINOv3Embedding:
    def __init__(self, model_name=IMAGE_EMBEDDER_MODEL, token=HF_TOKEN, dim=384):
        self.model = AutoModel.from_pretrained(model_name, token=token)
        self.processor = AutoImageProcessor.from_pretrained(model_name, token=token)
        self._ndims = dim
        self.logger = getLogger(__name__)
        # Configure logger
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger.debug(f"DINOv3Embedding initialized with model: {model_name}, dim: {dim}")

    def ndims(self):
        self.logger.debug(f"Returning embedding dimensions: {self._ndims}")
        return self._ndims

    def compute_embeddings(self, sources: List[Optional[str]]) -> List[Optional[List[float]]]:
        self.logger.debug(f"Computing embeddings for sources: {sources}")
        non_none_indices = [i for i, src in enumerate(sources) if src is not None]
        non_none_sources = [sources[i] for i in non_none_indices]

        if not non_none_sources:
            self.logger.debug("No valid sources provided for embedding computation.")
            return [None] * len(sources)

        imgs = [Image.open(src) for src in non_none_sources]
        self.logger.debug(f"Loaded {len(imgs)} images for embedding computation.")
        inputs = self.processor(images=imgs, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)
            cls_embs = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            self.logger.debug(f"Computed embeddings for {len(cls_embs)} images.")

        embeddings = [None] * len(sources)
        for idx, emb in zip(non_none_indices, cls_embs):
            embeddings[idx] = emb.tolist()

        self.logger.debug(f"Final embeddings created for {len(embeddings)} sources.")
        return embeddings


class MultimodalDB:
    def __init__(self, uri=DB_URI, table_name=TABLE_NAME, embedder_model=EMBEDDER_MODEL, image_embedder_model=IMAGE_EMBEDDER_MODEL):
        self.logger = getLogger(__name__)
        self.logger.debug(f"Initializing MultimodalDB with URI: {uri}, Table: {table_name}")
        self.db = lancedb.connect(uri)
        self.embedder = get_registry().get("huggingface").create(name=embedder_model)
        self.image_embedder = DINOv3Embedding(model_name=image_embedder_model)
        self.Schema = self.get_schema(self.embedder, image_embedder=self.image_embedder)

        if table_name in self.db.table_names():
            self.logger.debug(f"Opening existing table: {table_name}")
            self.table = self.db.open_table(table_name)
        else:
            self.logger.debug(f"Creating new table: {table_name}")
            self.table = self.db.create_table(table_name, schema=self.Schema, mode="overwrite")

        self.table.create_fts_index("text", replace=True)
        self.logger.debug("Full-text search index created for 'text' column.")

    def get_schema(self, text_embedder, image_embedder):
        self.logger.debug("Defining schema for the database.")
        class Schema(LanceModel):
            pk: str = Field(default_factory=lambda: uuid.uuid4().hex)  # Add primary key
            text: Optional[str] = text_embedder.SourceField(default=None)
            text_vector: Vector(text_embedder.ndims()) = text_embedder.VectorField()
            image_path: Optional[str]
            image_vector: Optional[Vector(image_embedder.ndims())]
            file_path: Optional[str]

        return Schema

    def add_entries(self, entries: List[dict]):
        self.logger.debug(f"Adding entries to the database: {entries}")
        for entry in entries:
            if "file_path" in entry and entry["file_path"]:
                self.logger.debug(f"Computing image embedding for entry: {entry['file_path']}")
                image_embedding = self.image_embedder.compute_embeddings([entry["file_path"]])[0]
                entry["image_vector"] = image_embedding
            else:
                self.logger.debug("No file_path provided or empty, setting image_vector to None.")
                entry["image_vector"] = None

        self.table.add(entries)
        self.logger.debug("Entries added successfully.")
        sample = self.table.to_pandas()
        print("SAMPLE ROWS:\n", sample)

        # 2. Try printing schema information (best-effort — API varies with lancedb versions)
        try:
            print("TABLE SCHEMA (repr):", getattr(self.table, "schema", None))
            # fallback: try ._schema or ._meta if available
            print("TABLE ATTRS:", {k: getattr(self.table, k) for k in dir(self.table) if "schema" in k.lower() or "meta" in k.lower()})
        except Exception as e:
            print("Could not fetch table.schema via attribute: ", e)

    def delete_entry(self, condition: str):
        self.logger.debug(f"Deleting entries with condition")
        self.table.delete(condition)
        self.logger.debug("Entries deleted successfully.")

    def update_entries(self, where: str, values: dict = None, values_sql: dict = None):
        self.logger.debug(f"Updating entries with condition: {where}, values: {values}, values_sql")
        if values and "file_path" in values and values["file_path"]:
            self.logger.debug(f"Computing image embedding for updated image path: {values['file_path']}")
            image_embedding = self.image_embedder.compute_embeddings([values["file_path"]])[0]
            values["image_vector"] = image_embedding
        elif values and "file_path" in values and not values["file_path"]:
            values["image_vector"] = None

        self.table.update(where=where, values=values, values_sql=values_sql)
        self.logger.debug("Entries updated successfully.")

    def drop_table(self):
        self.logger.debug(f"Dropping table: {TABLE_NAME}")
        self.db.drop_table(TABLE_NAME)
        self.logger.debug("Table dropped successfully.")

    def hybrid_search_with_rerank(self, query: str, top_k: int = 10):
        self.logger.debug(f"Performing hybrid search with query: {query}, top_k: {top_k}")
        reranker = RRFReranker()
        result = (
            self.table.search(query, query_type="hybrid",vector_column_name="text_vector",fts_columns=["text"])
            .rerank(reranker=reranker)
            .limit(top_k)
            .to_list()
        )
        self.logger.debug(f"Hybrid search results ")
        return result
    def image_search_by_pk(self, pk: str, top_k: int = 10):
        self.logger.debug(f"Performing image search by pk: {pk}, top_k: {top_k}")
        # Query the table to get the image_vector for the given pk
        result = self.table.search().where(f"pk = '{pk}'").limit(1).to_list()
        if not result:
            self.logger.error(f"No entry found for pk: {pk}")
            raise ValueError(f"No entry found for pk: {pk}")
        query_vec = result[0].get("image_vector")
        if query_vec is None:
            self.logger.error(f"No image_vector associated with pk: {pk}")
            raise ValueError(f"No image_vector associated with pk: {pk}")

        # Perform image search using the precomputed image_vector
        result = (
            self.table.search(query_vec, vector_column_name="image_vector", query_type="vector")
            .limit(top_k)
            .to_list()
        )
        # Filter out results with the same pk as the input and remove vector fields
        result = [res for res in result if res["pk"] != pk]
        for res in result:
            res.pop("text_vector", None)
            res.pop("image_vector", None)
        self.logger.debug(f"Image search results: {result[0] if result else 'None'}")
        return result
    def image_search(self, query_file_path: str, top_k: int = 10):
        self.logger.debug(f"Performing image search with query image path: {query_file_path}, top_k: {top_k}")
        query_vec = self.image_embedder.compute_embeddings([query_file_path])[0]
        if query_vec is None:
            self.logger.error("Failed to embed query image.")
            raise ValueError("Failed to embed query image.")
        result = (
            self.table.search(query_vec, vector_column_name="image_vector", query_type="vector") 
            .limit(top_k)
            .to_list()
        )
        for res in result:
            if "text_vector" in res:
                del res["text_vector"]
                del res["image_vector"]
        self.logger.debug(f"Image search results: {result[0]}")
        return result

def main():
    # Initialize DB
    db = MultimodalDB()

    # Sample data with text-only and text-image pairs
    data = [
        {"text": "hello world", "image_path": None, "file_path": None},
        {"text": "goodbye world", "image_path": None, "file_path": None},
        {"text": "mountain landscape", "image_path": "/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/utils/datasets/open_images_sample/0000a1b2fba255e9.jpg", "file_path": "/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/utils/datasets/open_images_sample/0000a1b2fba255e9.jpg"},
        {"text": "city skyline", "image_path": "/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/utils/datasets/open_images_sample/0000a4e648c5897f.jpg", "file_path": "/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/utils/datasets/open_images_sample/0000a4e648c5897f.jpg"},
        {"text": "beach scene", "image_path": "/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/utils/datasets/open_images_sample/0000a7dbcec8d6d1.jpg", "file_path": "/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/utils/datasets/open_images_sample/0000a7dbcec8d6d1.jpg"}
    ]

    print("\n✅ Adding entries...")
    db.add_entries(data)

    print("\n🔍 Image search with dummy image path:")
    query_image = "/home/seq_amal/work_temp/Celervus_temp/Celervus_AI/utils/datasets/open_images_sample/0000a1b2fba255e9.jpg"
    image_results = db.image_search(query_image, top_k=3)
    for idx, r in enumerate(image_results, start=1):
        print(f"{idx}. text: {r.get('text')}, image_path: {r.get('file_path')}")

if __name__ == "__main__":
    main()