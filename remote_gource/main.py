import asyncio
import arrow
import logging
from .sources.bitbucket import BitbucketSource
from .config import config
from .types import Commit, Author
from .gource import generate_video
from .gource.run import gource

logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig()


async def main():
    bitbucket_config = config['sources']['bitbucket'].get()
    source = BitbucketSource(bitbucket_config, {
        'date_start': arrow.get('2020-06-01')
    })

    await source.setup()
    commits = await source.get_commits()
    avatars_by_author = await source.get_avatars(list({commit.author for commit in commits}))
    await source.teardown()

    generate_video(commits, avatars_by_author)

asyncio.run(main())
