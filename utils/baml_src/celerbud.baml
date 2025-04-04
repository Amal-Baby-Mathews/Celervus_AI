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