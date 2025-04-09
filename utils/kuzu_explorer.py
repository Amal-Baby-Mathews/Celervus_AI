import cmd
import kuzu
from typing import Optional, List, Dict, Any
from kuzu_init import KuzuDBManager  # Adjust import based on your file structure

class KuzuDBExplorer(cmd.Cmd):
    """A CLI tool to explore a KuzuDB database."""
    intro = "Welcome to the KuzuDB Explorer. Type 'help' or '?' for commands.\nSpecify the database path with 'connect <path>'."
    prompt = "(kuzu) "

    def __init__(self):
        super().__init__()
        self.db_manager: Optional[KuzuDBManager] = None

    def do_connect(self, arg: str) -> None:
        """Connect to a KuzuDB database at the specified path. Usage: connect <path>"""
        if not arg:
            print("Error: Please provide a database path (e.g., './kuzu_db')")
            return
        try:
            self.db_manager = KuzuDBManager(db_path=arg, in_memory=False)
            print(f"Connected to database at {arg}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.db_manager = None

    def do_schema(self, arg: str) -> None:
        """Display the full schema of the database."""
        if not self._check_connection():
            return
        schema = self.db_manager.get_schema()
        print(schema)

    def do_nodes(self, arg: str) -> None:
        """List all nodes of a specified type. Usage: nodes <node_type>"""
        if not self._check_connection():
            return
        if not arg:
            print("Error: Please specify a node type (e.g., 'Topic', 'Subtopic')")
            return
        try:
            response = self.db_manager.conn.execute(f"MATCH (n:{arg}) RETURN n;")
            nodes = []
            while response.has_next():
                node_data = response.get_next()[0]  # Extract node properties
                nodes.append(f"ID: {node_data['id']}, Properties: {dict(node_data)}")
            if nodes:
                print(f"Nodes of type '{arg}':")
                for node in nodes:
                    print(f"  - {node}")
            else:
                print(f"No nodes found of type '{arg}'")
        except Exception as e:
            print(f"Error retrieving nodes: {e}")

    def do_node(self, arg: str) -> None:
        """Display details of a specific node by ID. Usage: node <node_type> <id>"""
        if not self._check_connection():
            return
        args = arg.split()
        if len(args) != 2:
            print("Error: Usage: node <node_type> <id> (e.g., 'node Topic t1')")
            return
        node_type, node_id = args
        try:
            response = self.db_manager.conn.execute(
                f"MATCH (n:{node_type} {{id: $id}}) RETURN n;",
                {"id": node_id}
            )
            if response.has_next():
                node_data = response.get_next()[0]
                print(f"Node Details ({node_type}, ID: {node_id}):")
                for key, value in node_data.items():
                    print(f"  {key}: {value}")
                self._show_relationships(node_type, node_id)
            else:
                print(f"No node found with type '{node_type}' and ID '{node_id}'")
        except Exception as e:
            print(f"Error retrieving node details: {e}")

    def _show_relationships(self, node_type: str, node_id: str) -> None:
        """Display relationships (branches) from a specific node."""
        try:
            # Outgoing relationships
            out_response = self.db_manager.conn.execute(
                f"MATCH (n:{node_type} {{id: $id}})-[r]->(m) RETURN type(r), m;",
                {"id": node_id}
            )
            outgoing = []
            while out_response.has_next():
                rel_type, target = out_response.get_next()
                outgoing.append(f"{rel_type} -> {target['id']} ({target.get('name', 'Unnamed')})")
            
            # Incoming relationships
            in_response = self.db_manager.conn.execute(
                f"MATCH (n:{node_type} {{id: $id}})<-[r]-(m) RETURN type(r), m;",
                {"id": node_id}
            )
            incoming = []
            while in_response.has_next():
                rel_type, source = in_response.get_next()
                incoming.append(f"{rel_type} <- {source['id']} ({source.get('name', 'Unnamed')})")

            if outgoing or incoming:
                print("Relationships:")
                if outgoing:
                    print("  Outgoing:")
                    for rel in outgoing:
                        print(f"    - {rel}")
                if incoming:
                    print("  Incoming:")
                    for rel in incoming:
                        print(f"    - {rel}")
            else:
                print("  No relationships found.")
        except Exception as e:
            print(f"Error retrieving relationships: {e}")

    def do_exit(self, arg: str) -> bool:
        """Exit the CLI."""
        if self.db_manager:
            del self.db_manager.conn
            del self.db_manager.db
            print("Disconnected from database.")
        print("Goodbye!")
        return True

    def _check_connection(self) -> bool:
        """Check if a database connection is established."""
        if self.db_manager is None:
            print("Error: Not connected to a database. Use 'connect <path>' first.")
            return False
        return True

if __name__ == "__main__":
    KuzuDBExplorer().cmdloop()