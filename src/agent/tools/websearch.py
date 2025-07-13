import httpx
import os
from typing import List
import asyncio

from agent.types.document import Document

# Load Google API credentials from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

class WebSearchTool:
    """
    A web search tool that uses the Google Custom Search API to retrieve relevant documents
    based on a list of queries. Results are deduplicated based on the URL.
    """

    async def run(self, queries: List[str]) -> List[Document]:
        """
        Executes web search for a list of queries concurrently and returns a flattened
        list of unique documents.

        Args:
            queries (List[str]): Search queries to run.

        Returns:
            List[Document]: A list of unique search result documents.
        """
        # Perform all search queries in parallel using asyncio.gather
        async with httpx.AsyncClient() as client:
            responses = await asyncio.gather(*[
                self._search(client, query) for query in queries
            ])

        # Step 1: Flatten results from all queries
        # Step 2: Deduplicate by URL
        docs = []
        seen_urls = set()
        for result in responses:
            for item in result:
                if item.url not in seen_urls:
                    docs.append(item)
                    seen_urls.add(item.url)

        return docs

    async def _search(self, client: httpx.AsyncClient, query: str) -> List[Document]:
        """
        Internal method to perform a single Google Custom Search request.

        Args:
            client (httpx.AsyncClient): Shared async HTTP client.
            query (str): A single search query string.

        Returns:
            List[Document]: Search result items converted to Document format.
        """
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query
        }

        # Call Google Search API
        resp = await client.get(url, params=params)
        data = resp.json()

        # Convert each search result item to a Document object
        docs = []
        for item in data.get("items", []):
            docs.append(Document(
                title=item.get("title"),
                snippet=item.get("snippet"),
                url=item.get("link")
            ))

        return docs
