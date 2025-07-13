from typing import NamedTuple

class Document(NamedTuple):
    """
    Represents a single web search result document.

    Attributes:
        title (str): The title of the document or web page.
        snippet (str): A short excerpt or summary describing the content.
        url (str): The full URL to the original source.
    """
    title: str
    snippet: str
    url: str
