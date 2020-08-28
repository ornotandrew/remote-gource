from typing import List
from remote_gource.types import Commit, Author
from remote_gource.gource.diff import parse_diff


def log_lines_from_commit(commit: Commit) -> str:
    """
    <unix_timestamp>|<committer_name>|<[M]odified/[A]dded/[D]eleted>|<path_to_touched_file>
    """
    touched_files = parse_diff(commit.diff)
    return [
        # prepend the repo name to each path
        f'{commit.timestamp}|{commit.author.name}|{f.action}|{commit.repo}/{f.path}'
        for f in touched_files
    ]


def log_from_commits(commits: List[Commit]) -> str:
    lines = [line for file in [log_lines_from_commit(commit) for commit in commits] for line in file]
    lines = sorted(lines)
    return '\n'.join(lines)
