class GraphSchema {
  nodes string[] @description("List of node types with properties, e.g., 'Topic { id (STRING, PK), name (STRING) }'")
  relationships string[] @description("List of relationship types with connections and properties, e.g., 'SUBTOPIC_OF (Subtopic -> Topic) { position (UINT32) }'")
  properties string[] @description("List of property definitions across nodes and relationships, e.g., 'id (STRING, PK)'")
}

class GraphQuery {
  query string @description("The OpenCypher query to execute")
}

class GraphResult {
  result string @description("The raw result from the graph database query")
}

class FinalResponse {
  answer string @stream.with_state @description("Natural language answer based on the query results")
  queryUsed string @stream.done @description("The Cypher query that was used")
  rawResults string @stream.done @description("The raw results that were returned")
}
function GenerateJsonQuery(schema: GraphSchema, question: string) -> GraphQuery {
  client GeminiGroqFallback
  prompt #"
function GenerateGraphQuery(schema: GraphSchema, question: string) -> GraphQuery {
  client GeminiGroqFallback
  prompt #"
function GenerateGraphQuery(schema: GraphSchema, question: string) -> GraphQuery {
  client GeminiGroqFallback
  prompt #"
    You are a graph database expert. Generate an OpenCypher query based on the user's question and the available schema.
    Keep the query simple, focused on answering the specific question, and valid for KuzuDB.
    ### Few-Shot Examples:
    1. **Question**: "What is the name of the person with ID 'p1'?"
       **Query**: "MATCH (p:JSON_Person {id: 'p1'}) RETURN p.name"

    2. **Question**: "List all people older than 30."
       **Query**: "MATCH (p:JSON_Person) WHERE p.age > 30 RETURN p.name, p.age"

    3. **Question**: "Which people have a health insurance provider named 'Blue Cross Blue Shield'?"
       **Query**: "MATCH (p:JSON_Person) WHERE ANY(ip IN p.info.insurance_provider WHERE ip.name = 'Blue Cross Blue Shield') RETURN p.name"

    4. **Question**: "How many people have a height greater than 1.7 meters?"
       **Query**: "MATCH (p:JSON_Person) WHERE p.info.height > 1.7 RETURN COUNT(p) AS tall_people"

    5. **Question**: "What are the names and policy numbers of people with health insurance?"
       **Query**: "MATCH (p:JSON_Person) WHERE ANY(ip IN p.info.insurance_provider WHERE ip.type = 'health') RETURN p.name, [ip IN p.info.insurance_provider WHERE ip.type = 'health' | ip.policy_number] AS policy_numbers"

    6. **Question**: "Which people are connected to the condition 'Diabetes'?"
       **Query**: "MATCH (p:JSON_Person)-[:HAS_CONDITION]->(c:JSON_Condition {name: 'Diabetes'}) RETURN p.name, c.name"

    7. **Question**: "List all conditions with the number of people affected, sorted by count."
       **Query**: "MATCH (p:JSON_Person)-[:HAS_CONDITION]->(c:JSON_Condition) RETURN c.name, COUNT(p) AS affected_count ORDER BY affected_count DESC"

    8. **Question**: "What people have names containing 'Greg'?"
       **Query**: "MATCH (p:JSON_Person) WHERE p.name CONTAINS 'Greg' RETURN p.name, p.id"

    9. **Question**: "Who has been affected by a condition since before 2018?"
       **Query**: "MATCH (p:JSON_Person)-[r:HAS_CONDITION]->(c:JSON_Condition) WHERE r.since < 2018 RETURN p.name, c.name, r.since"

    10. **Question**: "What are all the properties of the person with ID 'p2'?"
        **Query**: "MATCH (p:JSON_Person {id: 'p2'}) RETURN p"
    Available Schema:
    Nodes: {{ schema.nodes | join(', ') }}
    Relationships: {{ schema.relationships | join(', ') }}
    Properties: {{ schema.properties | join(', ') }}
    ### Instructions:
    - Use exact node labels (e.g., 'Topic', 'Subtopic') and relationship types (e.g., 'SUBTOPIC_OF') from the schema.
    - Match properties exactly as listed (e.g., 'id', 'name', 'text').
    - For text searches, use 'CONTAINS' for partial matches.
    - Return only the relevant data to answer the question.
    - Avoid invalid functions like 'TYPE' (use 'type(r)' only if explicitly needed and supported).

    {{ ctx.output_format }}

    {{ _.role("user") }} {{ question }}
  "#
}
function GenerateGraphQuery(schema: GraphSchema, question: string) -> GraphQuery {
  client GeminiGroqFallback
  prompt #"
function GenerateGraphQuery(schema: GraphSchema, question: string) -> GraphQuery {
  client GeminiGroqFallback
  prompt #"
function GenerateGraphQuery(schema: GraphSchema, question: string) -> GraphQuery {
  client GeminiGroqFallback
  prompt #"
    You are a graph database expert. Generate an OpenCypher query based on the user's question and the available schema.
    Keep the query simple, focused on answering the specific question, and valid for KuzuDB.

    Available Schema:
    Nodes: {{ schema.nodes | join(', ') }}
    Relationships: {{ schema.relationships | join(', ') }}
    Properties: {{ schema.properties | join(', ') }}

    ### Few-Shot Examples:
    1. **Question**: "What is the name of the topic with ID 'ff0e7064-dcc9-4b00-a712-28b703574ba4'?"
       **Query**: "MATCH (t:Topic {id: 'ff0e7064-dcc9-4b00-a712-28b703574ba4'}) RETURN t.name"

    2. **Question**: "What subtopics are under the topic 'Barcode Scanning Procedure: Align and Capture Barcode Data'?"
       **Query**: "MATCH (t:Topic {name: 'Barcode Scanning Procedure: Align and Capture Barcode Data'})<-[:SUBTOPIC_OF]-(s:Subtopic) RETURN s.name, s.text"

    3. **Question**: "Which topics have subtopics mentioning 'barcode'?"
       **Query**: "MATCH (t:Topic)<-[:SUBTOPIC_OF]-(s:Subtopic) WHERE s.text CONTAINS 'barcode' RETURN t.name"

    4. **Question**: "List all topics with their subtopic counts."
       **Query**: "MATCH (t:Topic)<-[:SUBTOPIC_OF]-(s:Subtopic) RETURN t.name, COUNT(s) AS subtopic_count"

    5. **Question**: "What are the bullet points for subtopics under 'Barcode Scanning Procedure: Align and Capture Barcode Data'?"
       **Query**: "MATCH (t:Topic {name: 'Barcode Scanning Procedure: Align and Capture Barcode Data'})<-[:SUBTOPIC_OF]-(s:Subtopic) RETURN s.bullet_points"

    ### Instructions:
    - Use exact node labels (e.g., 'Topic', 'Subtopic') and relationship types (e.g., 'SUBTOPIC_OF') from the schema.
    - Match properties exactly as listed (e.g., 'id', 'name', 'text').
    - For text searches, use 'CONTAINS' for partial matches.
    - Return only the relevant data to answer the question.
    - Avoid invalid functions like 'TYPE' (use 'type(r)' only if explicitly needed and supported).

    {{ ctx.output_format }}

    {{ _.role("user") }} {{ question }}
  "#
}

function AnalyzeResults(question: string, query: string, results: GraphResult) -> FinalResponse {
  client GeminiGroqFallback
  prompt #"
    Analyze the results from the graph database query and provide a natural language response.
    Explain the findings clearly and conversationally.

    Original Question: {{ question }}
    Query Used: {{ query }}
    Query Results: {{ results.result }}

    {{ ctx.output_format }}
  "#
}

test TestGenerateGraphQuery {
  functions [GenerateGraphQuery]
  args {
    schema {
      nodes ["Person", "Movie"]
      relationships ["ACTED_IN", "DIRECTED"]
      properties ["name", "title", "year"]
    }
    question "Who directed movies in 2020?"
  }
}

test TestAnalyzeResults {
  functions [AnalyzeResults]
  args {
    question "Who directed movies in 2020?"
    query "MATCH (p:Person)-[:DIRECTED]->(m:Movie) WHERE m.year = 2020 RETURN p.name, m.title"
    results {
      result "[{'p.name': 'Christopher Nolan', 'm.title': 'Tenet'}]"
    }
  }
}