import asyncio
import json
import logging
import math
import os
from datetime import timedelta

import aiohttp
import arrow

from remote_gource.sources.bitbucket.pagination import Pagination
from remote_gource.sources.bitbucket.utils import AuthToken, get_session
from remote_gource.sources.remote_source import AbstractRemoteSource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class BitbucketSource(AbstractRemoteSource):
    """
    Unfortunately, there doesn't seem to be a python client library for Bitbucket which

    - is not abandoned
    - supports the v2 api

    So this class calls the API manually. Docs are available here:

        https://developer.atlassian.com/bitbucket/api/2/reference/resource/
    """

    def __init__(self, config: dict, filters: dict = {}):
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.workspace = config['workspace']

        self.base_url = f'https://api.bitbucket.org/2.0/repositories/{self.workspace}'
        self.filters = filters

    async def setup(self):
        token: AuthToken = await get_session(self.client_id, self.client_secret)
        self.client = aiohttp.ClientSession(headers={'Authorization': f"Bearer {token['access_token']}"})

    async def teardown(self):
        await self.client.close()

    async def get_repos(self):
        log.info("Listing repos...")
        repos = await Pagination(self.client, f'{self.base_url}', self.filters, ['slug', 'updated_on']).get_all()
        # the api doesn't support filtering by 'updated_on', so we do that ourselves
        if 'date_start' in self.filters:
            repos = [r for r in repos if arrow.get(r['updated_on']).date() >= self.filters['date_start'].date()]
        if 'date_end' in self.filters:
            repos = [r for r in repos if arrow.get(r['updated_on']).date() <= self.filters['date_end'].date()]

        return repos

    async def get_commits_for_repo(self, repo_slug):
        log.debug(f'[{repo_slug}] Processing...')
        metadata = await Pagination(
            self.client,
            f'{self.base_url}/{repo_slug}/commits',
            self.filters,
            ['date', 'hash', 'author.user.display_name', 'author.user.nickname', 'author.user.links.avatar.href']
        ).get_all()

        total_commits_found = len(metadata)

        # the api doesn't support filtering by 'date', so we do that ourselves :(
        # https://community.developer.atlassian.com/t/how-do-i-filter-list-of-commits-from-rest-api-v2/15805/11
        log.debug(metadata[0])
        if 'date_start' in self.filters:
            metadata = [i for i in metadata if arrow.get(i['date']).date() >= self.filters['date_start'].date()]
        if 'date_end' in self.filters:
            metadata = [i for i in metadata if arrow.get(i['date']).date() <= self.filters['date_end'].date()]

        log.debug(f'[{repo_slug}] Found {total_commits_found} commits, filtered to {len(metadata)}')

        async def populate_diff(commit):
            resp = await self.client.get(f"{self.base_url}/{repo_slug}/diff/{commit['hash']}")
            commit['diff'] = await resp.text()

        log.debug(f'[{repo_slug}] Attaching diffs')
        await asyncio.gather(*[populate_diff(commit) for commit in metadata])

        return metadata

    async def get_commits(self):
        repos = await self.get_repos()
        log.info(f'Processing {len(repos)} repos')
        commits_by_repo = await asyncio.gather(*[self.get_commits_for_repo(repo['slug'])
                                                 for repo in repos[:1]])  # TODO remove the slice
        print(commits_by_repo[0][0])
