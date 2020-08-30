import os
import typing

from .types import Author


def write_log(path, log: str):
    path = os.path.expanduser(path)
    base_path = os.path.dirname(path)
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    with open(path, 'w') as f:
        f.write(log)


def write_avatars(dirname, avatars_by_author: typing.Dict[Author, bytes]):
    dirname = os.path.expanduser(dirname)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    for author, image in avatars_by_author.items():
        with open(os.path.join(dirname, author.name), 'wb') as f:
            f.write(image)
