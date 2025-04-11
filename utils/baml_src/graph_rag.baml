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
### Placeholder Definitions:
    - <NODE_TYPE>: The type of node (e.g., 'JSON_Person', 'JSON_Condition') from the schema.
    - <PROPERTY>: A property of a node or relationship (e.g., 'name', 'age', 'id') from the schema.
    - <VALUE>: A specific value from the user's question (e.g., 'p1', '30', 'Diabetes').
    - <REL_TYPE>: A relationship type (e.g., 'HAS_CONDITION') from the schema.
    - <NESTED_PROPERTY>: A property within a nested structure (e.g., 'info.height', 'insurance_provider.name').
    - <AGGREGATE>: An aggregation function (e.g., 'COUNT', 'SUM').

    ### Few-Shot Examples:
    1. **Question**: "What is the <PROPERTY> of the <NODE_TYPE> with ID '<VALUE>'?"
       **Query**: "MATCH (n:<NODE_TYPE> {id: '<VALUE>'}) RETURN n.<PROPERTY>"
       **Example**: "What is the name of the person with ID 'p1'?" -> "MATCH (n:JSON_Person {id: 'p1'}) RETURN n.name"

    2. **Question**: "List all <NODE_TYPE> where <PROPERTY> is greater than <VALUE>."
       **Query**: "MATCH (n:<NODE_TYPE>) WHERE n.<PROPERTY> > <VALUE> RETURN n.<PROPERTY>, n.<PROPERTY2>"
       **Example**: "List all people older than 30." -> "MATCH (n:JSON_Person) WHERE n.age > 30 RETURN n.name, n.age"

    3. **Question**: "Which <NODE_TYPE> have a <NESTED_PROPERTY> equal to '<VALUE>'?"
       **Query**: "MATCH (n:<NODE_TYPE>) WHERE ANY(x IN n.<NESTED_PROPERTY_PARENT> WHERE x.<NESTED_PROPERTY_CHILD> = '<VALUE>') RETURN n.<PROPERTY>"
       **Example**: "Which people have a health insurance provider named 'Blue Cross Blue Shield'?" -> "MATCH (n:JSON_Person) WHERE ANY(x IN n.info.insurance_provider WHERE x.name = 'Blue Cross Blue Shield') RETURN n.name"

    4. **Question**: "How many <NODE_TYPE> have <NESTED_PROPERTY> greater than <VALUE>?"
       **Query**: "MATCH (n:<NODE_TYPE>) WHERE n.<NESTED_PROPERTY> > <VALUE> RETURN <AGGREGATE>(n) AS result"
       **Example**: "How many people have a height greater than 1.7 meters?" -> "MATCH (n:JSON_Person) WHERE n.info.height > 1.7 RETURN COUNT(n) AS tall_people"

    5. **Question**: "What are the <PROPERTY1> and <NESTED_PROPERTY> of <NODE_TYPE> where <NESTED_PROPERTY_CHILD> is '<VALUE>'?"
       **Query**: "MATCH (n:<NODE_TYPE>) WHERE ANY(x IN n.<NESTED_PROPERTY_PARENT> WHERE x.<NESTED_PROPERTY_CHILD> = '<VALUE>') RETURN n.<PROPERTY1>, [x IN n.<NESTED_PROPERTY_PARENT> WHERE x.<NESTED_PROPERTY_CHILD> = '<VALUE>' | x.<NESTED_PROPERTY_CHILD2>] AS <NESTED_PROPERTY_CHILD2>s"
       **Example**: "What are the names and policy numbers of people with health insurance?" -> "MATCH (n:JSON_Person) WHERE ANY(x IN n.info.insurance_provider WHERE x.type = 'health') RETURN n.name, [x IN n.info.insurance_provider WHERE x.type = 'health' | x.policy_number] AS policy_numbers"

    6. **Question**: "Which <NODE_TYPE1> are connected to <NODE_TYPE2> with <PROPERTY> '<VALUE>' via <REL_TYPE>?"
       **Query**: "MATCH (n1:<NODE_TYPE1>)-[:<REL_TYPE>]->(n2:<NODE_TYPE2> {<PROPERTY>: '<VALUE>'}) RETURN n1.<PROPERTY1>, n2.<PROPERTY>"
       **Example**: "Which people are connected to the condition 'Diabetes'?" -> "MATCH (n1:JSON_Person)-[:HAS_CONDITION]->(n2:JSON_Condition {name: 'Diabetes'}) RETURN n1.name, n2.name"

    7. **Question**: "List all <NODE_TYPE2> with the <AGGREGATE> of <NODE_TYPE1> connected via <REL_TYPE>, sorted by <AGGREGATE>."
       **Query**: "MATCH (n1:<NODE_TYPE1>)-[:<REL_TYPE>]->(n2:<NODE_TYPE2>) RETURN n2.<PROPERTY>, <AGGREGATE>(n1) AS count ORDER BY count DESC"
       **Example**: "List all conditions with the number of people affected, sorted by count." -> "MATCH (n1:JSON_Person)-[:HAS_CONDITION]->(n2:JSON_Condition) RETURN n2.name, COUNT(n1) AS affected_count ORDER BY affected_count DESC"

    8. **Question**: "What <NODE_TYPE> have <PROPERTY> containing '<VALUE>'?"
       **Query**: "MATCH (n:<NODE_TYPE>) WHERE n.<PROPERTY> CONTAINS '<VALUE>' RETURN n.<PROPERTY>, n.<PROPERTY2>"
       **Example**: "What people have names containing 'Greg'?" -> "MATCH (n:JSON_Person) WHERE n.name CONTAINS 'Greg' RETURN n.name, n.id"

    9. **Question**: "Which <NODE_TYPE1> are related to <NODE_TYPE2> via <REL_TYPE> where <REL_PROPERTY> is less than <VALUE>?"
       **Query**: "MATCH (n1:<NODE_TYPE1>)-[r:<REL_TYPE>]->(n2:<NODE_TYPE2>) WHERE r.<REL_PROPERTY> < <VALUE> RETURN n1.<PROPERTY>, n2.<PROPERTY>, r.<REL_PROPERTY>"
       **Example**: "Who has been affected by a condition since before 2018?" -> "MATCH (n1:JSON_Person)-[r:HAS_CONDITION]->(n2:JSON_Condition) WHERE r.since < 2018 RETURN n1.name, n2.name, r.since"

    10. **Question**: "What are all the properties of the <NODE_TYPE> with <PROPERTY> '<VALUE>'?"
        **Query**: "MATCH (n:<NODE_TYPE> {<PROPERTY>: '<VALUE>'}) RETURN n"
        **Example**: "What are all the properties of the person with ID 'p2'?" -> "MATCH (n:JSON_Person {id: 'p2'}) RETURN n"

    ### Instructions:
    - Replace placeholders (<NODE_TYPE>, <PROPERTY>, <VALUE>, etc.) with specific values from the schema and question.
    - Use exact node labels, relationship types, and properties from the schema.
    - For text searches, use 'CONTAINS' for partial matches.
    - Use 'ANY' for filtering nested arrays.
    - Return only the relevant data, avoiding unnecessary complexity.
    - Support aggregations and sorting where requested.
    - Ensure queries are valid for KuzuDB.
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