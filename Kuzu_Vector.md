# Vector Search in KuzuDB: Technical Insights

## Overview
KuzuDB is a graph database that supports vector search through its `vector` extension, enabling similarity search over float array columns using an on-disk HNSW (Hierarchical Navigable Small World) index. This document captures technical details and lessons learned while integrating vector search into a knowledge graph application.

## Key Features
- **Vector Index**: 
  - Created with `CALL CREATE_VECTOR_INDEX('table_name', 'index_name', 'column_name', [option_name := option_value]);`.
  - Supports FLOAT[768] arrays (e.g., for `nomic-embed-text` embeddings) but currently limited to 32-bit floats (DOUBLE support pending).
  - Immutable once created; requires dropping and recreating to update.

- **Querying**: 
  - Performed via `CALL QUERY_VECTOR_INDEX('table_name', 'index_name', query_vector, k) RETURN node.id, distance ORDER BY distance;`.
  - Returns nearest neighbors based on a specified metric (e.g., cosine).

- **Supported Metrics**: 
  - `cosine`, `l2`, `l2sq`, `dotproduct`.
  - Configurable via `metric := 'value'` in index creation.

- **Options**:
  - `mu`: Max degree in upper graph layer (default: 30).
  - `ml`: Max degree in lower graph layer (default: 60).
  - `pu`: Upper graph sampling percentage (default: 0.05).
  - `efc`: Candidates considered during index construction (default: 200).
  - `efs`: Candidates considered during search (default: 200).

## Installation and Setup
- **Extension Loading**: 
  - Requires manual compilation from the KuzuDB GitHub repo (`make` in `kuzu/extension/vector/`).
  - Loaded with `LOAD EXTENSION '/path/to/vector.so';` (not an official extension, so `INSTALL vector;` alone fails).
  - Example:
    ```python
    self.conn.execute(f"LOAD EXTENSION '/path/to/kuzu/build/release/extension/vector/vector.so';")
    ```

- **Schema Integration**: 
  - Vector columns (e.g., `vector_embedding FLOAT[768]`) must be defined in node tables (e.g., `Topic`, `Subtopic`).
  - Comments (`--`) in `CREATE TABLE` statements cause parser errors; must be removed.

## Challenges Encountered
1. **Syntax Errors**:
   - Initial attempts used `CREATE VECTOR INDEX ... USING HNSW`, which failed (`Parser exception: Invalid input <CREATE VECTOR INDEX>`). Correct syntax uses `CALL CREATE_VECTOR_INDEX`.
   - Example fix:
     ```python
     self.conn.execute("CALL CREATE_VECTOR_INDEX('Topic', 'topic_vector_idx', 'vector_embedding', metric := 'cosine');")
     ```

2. **Duplicate Index Errors**:
   - `CALL CREATE_VECTOR_INDEX` doesn’t support `IF NOT EXISTS`, leading to `Binder exception: Index already exists`.
   - Workaround: Check existing indexes with `CALL SHOW_INDEXES()` before creation.
     ```python
     existing_indexes = set(row[0] for row in self.conn.execute("CALL SHOW_INDEXES() RETURN *;") if row)
     if "topic_vector_idx" not in existing_indexes:
         self.conn.execute("CALL CREATE_VECTOR_INDEX(...);")
     ```

3. **Segmentation Faults**:
   - Occurred post-request (e.g., after `/create_graph`), even with connection cleanup.
   - Likely a KuzuDB bug or extension incompatibility; mitigated by closing connections (`del self.conn; del self.db`) after operations, but not fully resolved.

4. **Empty Search Results**:
   - `/search/topics` and `/search/subtopics` returned no results despite existing data.
   - Causes:
     - Missing or invalid vector indexes (fixed by correct syntax).
     - Zeroed embeddings if `ollama.embeddings` failed (fallback `[0.0] * 768`).
   - Solution: Ensure `generate_embedding` works and indexes are created.

## Lessons Learned
- **Connection Management**: 
  - Unloading the database (`del self.db`) after operations reduces crash risk but requires reinitialization for subsequent requests (e.g., via `ensure_connection` method).
  - Example:
    ```python
    def close_connection(self):
        if self.conn: del self.conn
        if self.db: del self.db
    def ensure_connection(self):
        if not self.db: self.db = kuzu.Database(self.db_path)
    ```

- **Debugging**:
  - Logs (`logging.DEBUG`) and manual queries (e.g., `MATCH (t:Topic) RETURN t.vector_embedding`) are critical to verify embedding population and index status.
  - Core dumps (`gdb python core`) can pinpoint C++-level issues, though not fully explored here.

- **Version Compatibility**: 
  - Ensure the `kuzu` Python package and vector extension match (e.g., update with `pip install --upgrade kuzu` and rebuild extension).

## Current Status
- Vector search works when indexes are correctly created and embeddings are populated.
- Stability issues (segfaults) persist, likely requiring a KuzuDB bug report with version details and a reproducible case.

## Future Considerations
- Test alternative query methods (e.g., Cypher-based traversal) to bypass vector extension instability.
- Report segfaults to KuzuDB maintainers with core dump analysis.
- Explore connection pooling for performance if frequent reinitialization becomes a bottleneck.
