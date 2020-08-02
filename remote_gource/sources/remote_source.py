from abc import ABC, abstractmethod


class AbstractRemoteSource():
    @abstractmethod
    def get_commits(self, filters):
        pass
