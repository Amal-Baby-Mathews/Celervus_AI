// Define the structure for chat messages
class ChatMessage {
  role "user" | "assistant"
  content string
  timestamp string @description("ISO timestamp of when message was sent")
}

// Structure for context from various sources
class ContextSource {
  sourceType "vector_db" | "document" | "api"
  content string
  relevanceScore float @description("How relevant this context is to the query")
}

// Structure for the chatbot's response
class ChatResponse {
  answer string @description("The main response content")
  usedContext ContextSource[] @description("Sources used to generate the response")
  confidence "high" | "medium" | "low" @description("Confidence level in the response")
}
class CasualResponse {
  answer string @stream.with_state @description("Casual natural language response streamed token-by-token")
  queryUsed string @stream.done @description("Always 'NIL', returned when complete")
  rawResults string @stream.done @description("Always 'NIL', returned when complete")
}

function CasualGenerator(question: string) -> CasualResponse {
  client GeminiGroqFallback
  prompt #"
    Reply to the user in a casual, friendly manner based on the question provided.
    Use the context (if any) to provide a relevant answer. If the context lacks specific information or this is a general conversational query, acknowledge it and give a helpful, casual response.
    Always return the response in JSON format with the following schema:
    {
      answer: string,         // Your casual, friendly reply
      queryUsed: 'NIL',       // Set to 'NIL' since no database query is used
      rawResults: 'NIL'       // Set to 'NIL' since no raw results are generated
    }

    ### Examples:
    1. **Question**: 'Hello, how are you?'
       **Response**:
       {
         'answer': 'Hey there! I’m doing awesome, thanks for asking! How’s your day going?',
         'queryUsed': 'NIL',
         'rawResults': 'NIL'
       }

    2. **Question**: 'I didn’t get this line could you explain it?:The sky is blue because of light scattering.'
       **Response**:
       {
         'answer': 'No worries! That line means the sky looks blue because sunlight scatters when it hits tiny particles in the air—blue light spreads out more than other colors. Cool, right?',
         'queryUsed': 'NIL',
         'rawResults': 'NIL'
       }

    App details: Celervus is an advanced knowledge graph platform that transforms structured JSON data and unstructured PDF content into a dynamic, interconnected graph using KuzuDB, enabling real-time conversational queries and insights through its Celerbud AI interface powered by GraphRAG and BAML-driven natural language processing.

    {{ ctx.output_format }}

    {{ _.role("user") }} {{ question }}
  "#
}
// Main chat function with streaming
function StreamingChat(
  messages: ChatMessage[],
  context: ContextSource[]
) -> ChatResponse {
  client GeminiGroqFallback
  prompt #"
    You are a helpful AI assistant. Use the provided context to answer questions accurately.
    If the context doesn't contain relevant information, acknowledge that and provide a general response.

    Available Context:
    {% for ctx in context %}
    Source ({{ ctx.sourceType }}): {{ ctx.content }}
    {% endfor %}

    Chat History:
    {% for msg in messages %}
    {{ _.role(msg.role) }} {{ msg.content }}
    {% endfor %}

    {{ ctx.output_format }}
  "#
}
// Non-streaming chat function
function GenerateResponse(
  messages: ChatMessage[],
  context: ContextSource[]
) -> ChatResponse {
  client GeminiGroqFallback
  prompt #"
    You are a helpful AI assistant. Use the provided context to answer questions accurately.
    If the context doesn't contain relevant information, acknowledge that and provide a general response.

    Available Context:
    {% for ctx in context %}
    Source ({{ ctx.sourceType }}): {{ ctx.content }}
    {% endfor %}

    Chat History:
    {% for msg in messages %}
    {{ _.role(msg.role) }} {{ msg.content }}
    {% endfor %}
  "#
}
// New function for generating a document title
function GenerateDocumentTitle(text_chunks: string) -> string {
  client GeminiGroqFallback
  prompt #"
    You are a helpful AI assistant tasked with generating a concise title for a document.
    The title should be 5-10 words long, capturing the main theme of the text.
    Use the following text chunks from the document to determine the title:

    {{ text_chunks }}

    Provide only the title, without any additional explanation.
  "#
}

// New function for generating a subtopic name
function GenerateSubtopicName(subtopic_text: string) -> string {
  client GeminiGroqFallback
  prompt #"
    You are a helpful AI assistant tasked with generating a concise, descriptive name for a subtopic.
    The name should be 3-7 words long, capturing the key theme or subject matter.
    Use the following text excerpt from the subtopic to determine an appropriate name:

    {{ subtopic_text }}

    Provide only the subtopic name, without any additional explanation or leading/trailing punctuation.
  "#
}


function CheckSubtopicRelevance(text: string) -> float {
  client GeminiGroqFallback
  prompt #"
    Evaluate the relevance and substantiality of a potential subtopic text segment.
    Return a single decimal number between 0.0 and 1.0, where:
    - 0.0-0.3: Low relevance (disconnected sentences, purely navigational, or boilerplate content)
    - 0.4-0.7: Medium relevance (somewhat informative but lacking depth)
    - 0.8-1.0: High relevance (substantial, coherent discussion with meaningful details)

    Evaluation criteria:
    - Contains meaningful information
    - Discusses a coherent theme
    - Is not just boilerplate/formatting/references
    - Has sufficient detail

    {{ ctx.output_format }}

    {{ _.role("user") }} {{ text }}
  "#
}
class QueryIntent {
  requiresGraphQuery bool @description("Whether the query requires accessing a graph database")
  intentType "casual_conversation" | "graph_query" | "unknown" @description("The type of intent detected in the query")
  reasoning string @description("Explanation for why this classification was made")
}

function ClassifyQueryIntent(userQuery: string) -> QueryIntent {
  client GeminiGroqFallback
  prompt #"
    Determine if the given user query requires accessing a graph database or if it's just casual conversation.
    Consider queries about relationships between entities, data lookup, or structured information as requiring graph queries.
    Casual conversation includes greetings, small talk, or general questions not requiring data lookup.

    {{ ctx.output_format }}

    {{ _.role("user") }} {{ userQuery }}
  "#
}

test CasualConversationTest {
  functions [ClassifyQueryIntent]
  args {
    userQuery "Hello! How are you doing today?"
  }
}

test GraphQueryTest {
  functions [ClassifyQueryIntent]
  args {
    userQuery "Show me all employees who report to Sarah Johnson and have been at the company for more than 5 years."
  }
}
test BasicLowRelevanceTest {
  functions [CheckSubtopicRelevance]
  args {
    text "Click here to navigate to the next page. See also: Table of Contents."
  }
}

test HighRelevanceTest {
  functions [CheckSubtopicRelevance]
  args {
    text #"
      The photosynthesis process in plants consists of two main stages: light-dependent reactions and light-independent reactions. 
      During the light-dependent reactions, chlorophyll absorbs sunlight and converts it into chemical energy in the form of ATP and NADPH.
      The light-independent reactions, also known as the Calvin cycle, use this energy to produce glucose from carbon dioxide.
    "#
  }
}
// Test with a simple chat message
// Test with different context sources
test ChatWithVectorDBContext {
  functions [StreamingChat]
  args {
    messages [
      {
        role "user"
        content "What can you tell me about machine learning?"
        timestamp "2024-03-20T10:00:00Z"
      }
    ]
    context [
      {
        sourceType "vector_db"
        content "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed."
        relevanceScore 0.95
      }
    ]
  }
}

test ChatWithMultipleContextSources {
  functions [StreamingChat]
  args {
    messages [
      {
        role "user"
        content "How do neural networks work?"
        timestamp "2024-03-20T10:05:00Z"
      }
    ]
    context [
      {
        sourceType "vector_db"
        content "Neural networks are computing systems inspired by biological neural networks in human brains."
        relevanceScore 0.9
      },
      {
        sourceType "document"
        content "Deep learning neural networks typically consist of multiple layers of interconnected nodes."
        relevanceScore 0.85
      }
    ]
  }
}