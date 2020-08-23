import asyncio
import arrow
import logging
from .sources.bitbucket import BitbucketSource
from .config import config
from .types import Commit, Author
from .gource.log import log_from_commits

logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig()


async def main():
    bitbucket_config = config['sources']['bitbucket'].get()
    source = BitbucketSource(bitbucket_config, {
        'date_start': arrow.get('2020-07-31')
    })

    await source.setup()
    commits = await source.get_commits()
    await source.teardown()

    gource_log = log_from_commits(commits)
    print(gource_log)


asyncio.run(main())
