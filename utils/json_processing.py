import re
from typing import List, Optional, Dict, Any
# from api import shared_db_manager  # Import shared_db_manager from your FastAPI module
from kuzu_init import KuzuDBManager  # Ensure type hinting
import json
import os
import tempfile
from baml_client import b  # BAML client
from baml_client.types import GraphSchema, GraphQuery, GraphResult, FinalResponse
class JSONKnowledgeGraph:
    """Class to ingest JSON data into a KuzuDB knowledge graph and query it."""

    def __init__(self, db_manager: KuzuDBManager):
        """Initialize with a shared KuzuDBManager instance."""
        self.db_manager = db_manager
        self.baml_client = b  # Initialize BAML client
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

    def get_table_schema(self, table_id: int) -> str:
        """Retrieve the schema for a specific table by its ID as a structured string.

        Args:
            table_id (int): The ID of the table (from SHOW_TABLES).

        Returns:
            str: Structured string describing the schema (nodes, relationships, properties).
        """
        try:
            # Find the table name by ID
            response = self.db_manager.conn.execute("CALL SHOW_TABLES() RETURN *;")
            table_name = None
            table_type = None
            while response.has_next():
                table_info = response.get_next()
                if table_info[0] == table_id:
                    table_name = table_info[1]
                    table_type = table_info[2]
                    break
            
            if not table_name:
                raise ValueError(f"No table found with ID {table_id}.")
            
            # Get table properties
            prop_response = self.db_manager.conn.execute(f"CALL TABLE_INFO('{table_name}') RETURN *;")
            properties = []
            while prop_response.has_next():
                prop_info = prop_response.get_next()
                prop_detail = f"{prop_info[1]} ({prop_info[2]}{', PK' if prop_info[4] else ''})"
                properties.append(prop_detail)

            # Construct schema string
            schema_str = "Graph Schema:\n"
            if table_type == "NODE":
                schema_str += f"Nodes:\n  - {table_name} {{ {', '.join(properties)} }}\n"
                schema_str += "Relationships: None\n"
            elif table_type == "REL":
                conn_response = self.db_manager.conn.execute(f"CALL SHOW_CONNECTION('{table_name}') RETURN *;")
                if conn_response.has_next():
                    conn_info = conn_response.get_next()
                    schema_str += "Nodes: None\n"
                    schema_str += f"Relationships:\n  - {table_name} ({conn_info[0]} -> {conn_info[1]}) {{ {', '.join(properties)} }}\n"
                else:
                    schema_str += "Nodes: None\n"
                    schema_str += f"Relationships:\n  - {table_name} {{ {', '.join(properties)} }}\n"
            schema_str += f"Properties:\n" + "\n".join(f"  - {p}" for p in properties) if properties else "Properties: None"

            return schema_str

        except Exception as e:
            print(f"Error retrieving schema for table ID {table_id}: {e}")
            return "Graph Schema:\nNodes: None\nRelationships: None\nProperties: None"

    def query_graph_nlp(self, nlp_query: str, table_id: int) -> str:
        """Query the graph using NLP, converting to Cypher with BAML, for a specific table.

        Args:
            nlp_query (str): Natural language query.
            table_id (int): ID of the JSON-ingested table to query.

        Returns:
            str: Natural language response based on query results.
        """
        try:
            print(f"Received NLP query: '{nlp_query}' for table ID {table_id}")

            # Step 1: Retrieve schema for the specific table
            print(f"Retrieving schema for table ID {table_id}...")
            schema_str = self.get_table_schema(table_id)
            print(f"Schema retrieved:\n{schema_str}")

            # Parse schema into GraphSchema
            nodes = []
            relationships = []
            properties = []
            node_section = re.search(r"Nodes:\n(.*?)(?:\nRelationships:|$)", schema_str, re.DOTALL)
            if node_section and "None" not in node_section.group(1):
                for line in node_section.group(1).splitlines():
                    if line.strip().startswith("- "):
                        nodes.append(line.strip()[2:])
            rel_section = re.search(r"Relationships:\n(.*?)(?:\nProperties:|$)", schema_str, re.DOTALL)
            if rel_section and "None" not in rel_section.group(1):
                for line in rel_section.group(1).splitlines():
                    if line.strip().startswith("- "):
                        relationships.append(line.strip()[2:])
            prop_section = re.search(r"Properties:\n(.*)", schema_str, re.DOTALL)
            if prop_section and "None" not in prop_section.group():
                for line in prop_section.group(1).splitlines():
                    if line.strip().startswith("- "):
                        properties.append(line.strip()[2:])

            schema = GraphSchema(nodes=nodes, relationships=relationships, properties=properties)
            print(f"Parsed schema: Nodes - {schema.nodes}, Relationships - {schema.relationships}")

            if not schema.nodes and not schema.relationships:
                return f"Error: No schema found for table ID {table_id}."

            # Step 2: Generate Cypher query with BAML
            print("Generating Cypher query with BAML...")
            graph_query: GraphQuery = self.baml_client.GenerateJsonQuery(question=nlp_query, schema=schema)
            cypher_query = graph_query.query
            print(f"Generated Cypher query: {cypher_query}")
            if not cypher_query:
                return "Error: Failed to generate a valid Cypher query."

            # Step 3: Execute the query
            print("Executing Cypher query...")
            response = self.db_manager.conn.execute(cypher_query)
            result_data = []
            while response.has_next():
                result_data.append(response.get_next())
            result_str = "\n".join([str(row) for row in result_data]) if result_data else "No results found."
            print(f"Query results: {result_str}")
            graph_result = GraphResult(result=result_str)

            # Step 4: Analyze results with BAML
            print("Analyzing results with BAML...")
            final_response: FinalResponse = self.baml_client.AnalyzeResults(
                question=nlp_query,
                query=cypher_query,
                results=graph_result
            )
            print(f"Final response: {final_response.answer}")
            return final_response.answer

        except Exception as e:
            print(f"Error processing NLP query '{nlp_query}' for table ID {table_id}: {e}")
            return f"Error: Unable to process query due to {str(e)}"
    def list_json_nodes(self, json_only: bool = True) -> List[Dict[str, Any]]:
        """List all node tables in the database with their IDs, optionally filtering to those created by JSON ingestion.

        Args:
            json_only (bool): If True, only return tables tagged as JSON-ingested (default: True).

        Returns:
            List[Dict[str, Any]]: List of dictionaries with 'id' and 'name' for each node table.
        """
        try:
            # Use SHOW_TABLES to get all tables
            response = self.db_manager.conn.execute("CALL SHOW_TABLES() RETURN *;")
            tables = []

            while response.has_next():
                table_info = response.get_next()
                table_id = table_info[0]  # Column 0 is the table ID
                table_name = table_info[1]  # Column 1 is the table name
                table_type = table_info[2]  # Column 2 is the table type (NODE or REL)

                # Filter for node tables
                if table_type == "NODE":
                    # Check if table is JSON-ingested (tagged with "JSON_" prefix)
                    is_json_table = table_name.startswith("JSON_")
                    if not json_only or (json_only and is_json_table):
                        tables.append({"id": table_id, "name": table_name})

            return tables
        except Exception as e:
            print(f"Error listing node tables: {e}")
            return []
    def get_json_table_nodes(self, table_id: int, id: Optional[str] = None, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve nodes from a specific JSON-ingested table by table ID.

        Args:
            table_id (int): The ID of the JSON-ingested table (e.g., 3 for 'JSON_Person').
            id (Optional[str]): The ID to filter nodes by (exact match).
            name (Optional[str]): The name to filter nodes by (exact match).

        Returns:
            List[Dict[str, Any]]: List of nodes (as dictionaries) matching the criteria.

        Raises:
            ValueError: If the table ID does not correspond to a JSON-ingested node table.
        """
        try:
            # Get all tables and find the one matching the table_id
            response = self.db_manager.conn.execute("CALL SHOW_TABLES() RETURN *;")
            table_name = None
            while response.has_next():
                table_info = response.get_next()
                if table_info[0] == table_id and table_info[2] == "NODE":
                    table_name = table_info[1]  # Column 1 is the table name
                    if not table_name.startswith("JSON_"):
                        raise ValueError(f"Table with ID {table_id} ('{table_name}') is not a JSON-ingested table.")
                    break
            
            if table_name is None:
                raise ValueError(f"No node table found with ID {table_id}.")

            # Build the Cypher query based on filters
            query = f"MATCH (n:{table_name})"
            conditions = []
            params = {}
            if id:
                conditions.append("n.id = $id")
                params["id"] = id
            if name:
                conditions.append("n.name = $name")
                params["name"] = name
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " RETURN n;"

            # Execute the query
            response = self.db_manager.conn.execute(query, params)
            nodes = []
            while response.has_next():
                node_data = response.get_next()[0]  # First column is the node
                nodes.append({key: value for key, value in node_data.items()})

            return nodes

        except ValueError as ve:
            print(f"Error: {ve}")
            raise
        except Exception as e:
            print(f"Error retrieving nodes from table with ID {table_id}: {e}")
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