import asyncio
import logging

from .config import get_config
from .gource.log import log_from_commits
from .sources.bitbucket import BitbucketSource
from .utils import write_log, write_avatars

logging.basicConfig(level=logging.DEBUG)


async def main():
    config = get_config()
    log_file_path = config['log_file_path']
    user_images_dir = config['user_images_dir']
    filters = config['filters']
    bitbucket_config = config['sources']['bitbucket']

    source = BitbucketSource(bitbucket_config, filters)

    await source.setup()
    commits = await source.get_commits()
    avatars_by_author = await source.get_avatars(list({commit.author for commit in commits}))
    await source.teardown()

    write_log(log_file_path, log_from_commits(commits))
    write_avatars(user_images_dir, avatars_by_author)


if __name__ == '__main__':
    asyncio.run(main())
