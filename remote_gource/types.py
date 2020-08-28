from typing import List
import arrow


class Author:
    name: str
    avatar_url: str

    def __init__(self, name, avatar_url):
        self.name = name
        self.avatar_url = avatar_url

    def __hash__(self):
        return hash((self.name, self.avatar_url))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)


class Commit:
    repo: str
    timestamp: int
    hash: str
    author: Author
    diff: str

    def __init__(self, repo: str, timestamp: int, hash: str, author: Author, diff: str):
        self.repo = repo
        self.timestamp = timestamp
        self.hash = hash
        self.author = author
        self.diff = diff
