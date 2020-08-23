import logging
from typing import List
from unidiff import PatchSet, PatchedFile

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Action:
    modified = 'M'
    added = 'A'
    deleted = 'D'

    @classmethod
    def from_patched_file(cls, patched_file: PatchedFile):
        if patched_file.is_added_file:
            return cls.added
        if patched_file.is_removed_file:
            return cls.deleted

        # includes modified and renamed files
        return cls.modified


class TouchedFile:
    action: Action
    path: str

    def __init__(self, action, path):
        self.action = action
        self.path = path


def parse_diff(diff: str) -> List[TouchedFile]:
    files = PatchSet(diff)

    # remove files which we can't deal with
    files = [f for f in files if not f.is_binary_file]

    return [
        TouchedFile(
            action=Action.from_patched_file(f),
            path=f.target_file[len('b/'):]
        ) for f in files
    ]
