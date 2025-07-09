from agent.nodes.reflect import reflect
from agent.types.document import Document

question = "Explain black holes like I'm five."

docs = [
    Document(
        title="What Is a Black Hole? Simple Explanation",
        snippet="A black hole is a place in space where gravity is so strong that nothing—not even light—can escape from it.",
        url="https://bluelife.in/article/astrophysics/black_hole/"
    )
]

result = reflect(question, docs)
print("\nReflect Result:")
print(result)
