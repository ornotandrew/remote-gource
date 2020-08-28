from typing import List
from remote_gource.types import Commit
from .log import log_from_commits
from .run import gource


def generate_video(commits: List[Commit], avatars_by_author):
    custom_log_lines = log_from_commits(commits)
    gource(custom_log_lines, avatars_by_author, {})
