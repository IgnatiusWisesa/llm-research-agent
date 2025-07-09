from agent.nodes.synthesize import synthesize
from agent.types.document import Document

question = "Explain black holes like I'm five."

docs = [
    Document(
        title="What Is a Black Hole?",
        snippet="A black hole is a place in space where gravity is so strong that nothing—not even light—can escape.",
        url="https://example.com/black-hole"
    )
]

answer = synthesize(question, docs)
print("\nSynthesized Answer:\n")
print(answer)
