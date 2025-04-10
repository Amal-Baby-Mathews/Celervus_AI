import re
from typing import List, Optional, Dict, Any
# from api import shared_db_manager  # Import shared_db_manager from your FastAPI module
from kuzu_init import KuzuDBManager  # Ensure type hinting
import json
import os
import tempfile

class JSONKnowledgeGraph:
    """Class to ingest JSON data into a KuzuDB knowledge graph and query it."""

    def __init__(self, db_manager: KuzuDBManager):
        """Initialize with a shared KuzuDBManager instance."""
        self.db_manager = db_manager
        # Ensure JSON extension is loaded
        try:
            # self.db_manager.conn.execute("INSTALL json;")
            self.db_manager.conn.execute("LOAD json;")
            print("JSON extension installed and loaded.")
        except Exception as e:
            print(f"Warning: Failed to install/load JSON extension: {e}. Assuming already loaded.")

    def ingest_json_file(self, file_path: str, node_table: str = "Node", rel_table: Optional[str] = None) -> None:
        """Ingest a JSON file into KuzuDB.

        Args:
            file_path (str): Path to the JSON file.
            node_table (str): Name of the node table to create/copy into (default: 'Node').
            rel_table (Optional[str]): Name of the relationship table (if applicable).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        # Read JSON to determine structure
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Check if it’s a list (common for node/rel data)
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of objects.")

        # Dynamically infer schema from first object (assuming uniform structure)
        if data:
            first_item = data[0]
            if "from" in first_item and "to" in first_item and rel_table:
                self._ingest_relationship_json(file_path, rel_table)
            else:
                self._ingest_node_json(file_path, node_table)
        else:
            print("Warning: Empty JSON file. No data ingested.")

    def ingest_json_string(self, json_str: str, node_table: str = "Node", rel_table: Optional[str] = None) -> None:
        """Ingest a JSON string into KuzuDB.

        Args:
            json_str (str): JSON string to ingest.
            node_table (str): Name of the node table to create/copy into (default: 'Node').
            rel_table (Optional[str]): Name of the relationship table (if applicable).
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

        if not isinstance(data, list):
            raise ValueError("JSON string must contain a list of objects.")

        # Write to a temporary file to use COPY FROM
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data, temp_file)
            temp_file_path = temp_file.name

        try:
            if data and "from" in data[0] and "to" in data[0] and rel_table:
                self._ingest_relationship_json(temp_file_path, rel_table)
            else:
                self._ingest_node_json(temp_file_path, node_table)
        finally:
            os.unlink(temp_file_path)  # Clean up temporary file

    def _ingest_node_json(self, file_path: str, table_name: str) -> None:
        """Helper to ingest JSON into a node table with a JSON tag."""
        tagged_table_name = f"JSON_{table_name}"  # Prefix to identify JSON-ingested tables
        with open(file_path, 'r') as f:
            data = json.load(f)
            if not data:
                print(f"Warning: No data to ingest into {tagged_table_name}.")
                return
            sample = data[0]

        columns = [f"{key} STRING" for key in sample.keys()]
        primary_key = "id" if "id" in sample else list(sample.keys())[0]

        schema_query = f"""
            CREATE NODE TABLE IF NOT EXISTS {tagged_table_name} (
                {', '.join(columns)},
                PRIMARY KEY ({primary_key})
            );
        """
        try:
            self.db_manager.conn.execute(schema_query)
            self.db_manager.conn.execute(f"COPY {tagged_table_name} FROM '{file_path}';")
            print(f"Successfully ingested JSON into node table '{tagged_table_name}'.")
        except Exception as e:
            print(f"Error ingesting JSON into node table '{tagged_table_name}': {e}")

    def _ingest_relationship_json(self, file_path: str, table_name: str) -> None:
        """Helper to ingest JSON into a relationship table."""
        # Assume 'from' and 'to' reference existing node tables 'Node' and 'Node'
        # Adjust node table names if your schema differs
        schema_query = f"""
            CREATE REL TABLE IF NOT EXISTS {table_name} (
                FROM Node TO Node,
                {"since UINT16" if "since" in json.load(open(file_path, 'r'))[0] else ""}
            );
        """
        try:
            self.db_manager.conn.execute(schema_query)
            self.db_manager.conn.execute(f"COPY {table_name} FROM '{file_path}';")
            print(f"Successfully ingested JSON into relationship table '{table_name}'.")
        except Exception as e:
            print(f"Error ingesting JSON into relationship table '{table_name}': {e}")

    def query_graph_nlp(self, nlp_query: str) -> str:
        """Placeholder to query the graph using NLP, converting to Cypher.

        Args:
            nlp_query (str): Natural language query.

        Returns:
            str: Dummy response (to be developed later).
        """
        # Placeholder implementation
        print(f"Received NLP query: {nlp_query}")
        return f"Dummy response for query: '{nlp_query}'. Cypher conversion to be implemented."
    def list_json_nodes(self, json_only: bool = True) -> List[str]:
        """List all node tables in the database, optionally filtering to those created by JSON ingestion.

        Args:
            json_only (bool): If True, only return tables tagged as JSON-ingested (default: True).

        Returns:
            List[str]: List of node table names.
        """
        try:
            # Use SHOW_TABLES to get all tables
            response = self.db_manager.conn.execute("CALL SHOW_TABLES() RETURN *;")
            tables = []

            while response.has_next():#type: ignore
                table_info = response.get_next()#type: ignore
                table_name = table_info[1]  # Column 1 is the table name
                table_type = table_info[2]  # Column 2 is the table type (NODE or REL)

                # Filter for node tables
                if table_type == "NODE":
                    # Check if table is JSON-ingested (tagged with "JSON_" prefix)
                    is_json_table = table_name.startswith("JSON_")
                    if not json_only or (json_only and is_json_table):
                        tables.append(table_name)

            return tables
        except Exception as e:
            print(f"Error listing node tables: {e}")
            return []
if __name__ == "__main__":
    # # Example usage of JSONKnowledgeGraph
    # jkg = JSONKnowledgeGraph()

    # # Ingest a JSON file
    # try:
    #     jkg.ingest_json_file("people.json", node_table="Person")
    # except Exception as e:
    #     print(f"Error ingesting JSON file: {e}")

    # # Ingest a JSON string
    # json_str = '[{"id": "p4", "name": "John"}, {"id": "p5", "name": "Jane"}]'
    # try:
    #     jkg.ingest_json_string(json_str, node_table="Person")
    # except Exception as e:
    #     print(f"Error ingesting JSON string: {e}")

    # # Query with NLP (placeholder)
    # try:
    #     response = jkg.query_graph_nlp("Who has diabetes?")
    #     print(response)  # "Dummy response for query: 'Who has diabetes?'..."
    # except Exception as e:
    #     print(f"Error querying graph with NLP: {e}")
    pass