from typing import List
import arrow


class Author:
    name: str
    avatar_url: str

    def __init__(self, name, avatar_url):
        self.name = name
        self.avatar_url = avatar_url


class Commit:
    timestamp: int
    hash: str
    author: Author
    diff: str

    def __init__(self, timestamp: int, hash: str, author: Author, diff: str):
        self.timestamp = timestamp
        self.hash = hash
        self.author = author
        self.diff = diff
