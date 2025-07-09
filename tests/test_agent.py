import asyncio
from agent.types.document import Document
from agent.nodes.reflect import reflect

# Contoh dummy documents dari hasil Google
docs = [
    Document(
        title="Black Holes Explained Simply",
        snippet="Black holes are places in space where gravity pulls so much that even light cannot get out.",
        url="https://www.youtube.com/watch?v=lgnus1En1HM"
    ),
    Document(
        title="What is a Black Hole? (For Kids)",
        snippet="Black holes are very dense objects with strong gravity. They pull things in, even light.",
        url="https://www.youtube.com/watch?v=IDpjMIl-uYE"
    ),
]

question = "Explain black holes like I'm five."

async def main():
    summary = await reflect(question, docs)
    print("\n[Reflected Summary]\n")
    print(summary)

asyncio.run(main())
