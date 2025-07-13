# ✅ Import the main synthesis function and the document type
from agent.nodes.synthesize import synthesize
from agent.types.document import Document

# 🧠 Define the input question for the synthesis process
question = "Explain black holes like I'm five."

# 📄 Simulate a list of documents (normally this would come from web search)
docs = [
    Document(
        title="What Is a Black Hole?",
        snippet="A black hole is a place in space where gravity is so strong that nothing—not even light—can escape.",
        url="https://example.com/black-hole"
    )
]

# 🧪 Run the synthesis function to generate a simple answer with citation mapping
answer = synthesize(question, docs)

# 📤 Display the final answer
print("\nSynthesized Answer:\n")
print(answer)
