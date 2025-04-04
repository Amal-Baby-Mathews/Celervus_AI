class BulletPoints {
  points string[] @description("Array of clear, concise bullet points that capture the main ideas")
  mainIdea string @description("The central theme or main idea of the text")
  complexity "basic" | "intermediate" | "advanced" @description("The level of complexity of the content")
}

function ExtractBulletPoints(text: string) -> BulletPoints {
  client GeminiGroqFallback
  prompt #"
    Create a set of clear and concise bullet points from the given text. Focus on the key ideas and important details.
    Determine the main idea and assess the complexity level of the content.

    {{ ctx.output_format }}

    {{ _.role("user") }} {{ text }}
  "#
}

test SimpleSubtopicTest {
  functions [ExtractBulletPoints]
  args {
    text "Photosynthesis is the process by which plants convert sunlight into energy. During this process, plants take in carbon dioxide from the air and water from the soil. Using sunlight as energy, they convert these materials into glucose and oxygen. The glucose serves as food for the plant, while oxygen is released into the atmosphere as a byproduct."
  }
}

test ComplexSubtopicTest {
  functions [ExtractBulletPoints]
  args {
    text #"
      The Industrial Revolution marked a major turning point in human history. This period saw the transition from manual production methods to machine manufacturing. It began in Britain in the late 18th century and spread to other parts of the world. The revolution led to increased production capacity, urbanization, and significant social changes. Workers moved from rural areas to cities, working conditions were often harsh, and new social classes emerged. Technical innovations like the steam engine and power loom transformed manufacturing forever.
    "#
  }
}