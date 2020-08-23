from abc import ABC, abstractmethod
from typing import List
from remote_gource.types import Commit


class AbstractRemoteSource():
    @abstractmethod
    async def get_commits(self, filters) -> List[Commit]:
        pass
