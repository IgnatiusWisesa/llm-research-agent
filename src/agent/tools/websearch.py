import httpx
import os
from typing import List
import asyncio

from agent.types.document import Document

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

class WebSearchTool:
    async def run(self, queries: List[str]) -> List[Document]:
        async with httpx.AsyncClient() as client:
            responses = await asyncio.gather(*[
                self._search(client, query) for query in queries
            ])

        # Flatten and deduplicate
        docs = []
        seen_urls = set()
        for result in responses:
            for item in result:
                if item.url not in seen_urls:
                    docs.append(item)
                    seen_urls.add(item.url)
        return docs

    async def _search(self, client: httpx.AsyncClient, query: str) -> List[Document]:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query
        }
        resp = await client.get(url, params=params)
        data = resp.json()
        docs = []
        for item in data.get("items", []):
            docs.append(Document(
                title=item.get("title"),
                snippet=item.get("snippet"),
                url=item.get("link")
            ))
        return docs
