import asyncio
import json
import logging
import math
import os
from datetime import timedelta
from typing import List, Dict

import aiohttp
import arrow

from remote_gource.sources.bitbucket.pagination import Pagination
from remote_gource.sources.bitbucket.utils import AuthToken, get_session
from remote_gource.sources.remote_source import AbstractRemoteSource
from remote_gource.types import Commit, Author

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

        self.client = None  # is created in self.setup()

    async def setup(self):
        token: AuthToken = await get_session(self.client_id, self.client_secret)
        self.client = aiohttp.ClientSession(
            headers={'Authorization': f"Bearer {token['access_token']}"})

    async def teardown(self):
        await self.client.close()

    async def get_repos(self):
        log.info("Listing repos...")
        repos = await Pagination(self.client, f'{self.base_url}', self.filters, ['slug', 'updated_on']).get_all()
        # the api doesn't support filtering by 'updated_on', so we do that ourselves
        if 'date_start' in self.filters:
            repos = [r for r in repos if arrow.get(
                r['updated_on']).date() >= self.filters['date_start'].date()]
        if 'date_end' in self.filters:
            repos = [r for r in repos if arrow.get(
                r['updated_on']).date() <= self.filters['date_end'].date()]

        return repos

    async def get_commits_for_repo(self, repo_slug):
        log.debug(f'[{repo_slug}] Processing...')
        metadata = await Pagination(
            self.client,
            f'{self.base_url}/{repo_slug}/commits',
            self.filters,
            ['date', 'hash', 'author.user.display_name',
                'author.user.nickname', 'author.user.links.avatar.href']
        ).get_all()

        total_commits_found = len(metadata)

        # the api doesn't support filtering by 'date', so we do that ourselves :(
        # https://community.developer.atlassian.com/t/how-do-i-filter-list-of-commits-from-rest-api-v2/15805/11
        if 'date_start' in self.filters:
            metadata = [i for i in metadata if arrow.get(
                i['date']).date() >= self.filters['date_start'].date()]
        if 'date_end' in self.filters:
            metadata = [i for i in metadata if arrow.get(
                i['date']).date() <= self.filters['date_end'].date()]

        log.debug(
            f'[{repo_slug}] Found {total_commits_found} commits, filtered to {len(metadata)}')

        # fill out the diffs
        async def populate_diff(commit):
            resp = await self.client.get(f"{self.base_url}/{repo_slug}/diff/{commit['hash']}")
            commit['diff'] = (await resp.read()).decode()

        log.debug(f'[{repo_slug}] Attaching diffs')
        await asyncio.gather(*[populate_diff(commit) for commit in metadata])

        # attach the repo slug to the commit
        return [dict(**m, repo_slug=repo_slug) for m in metadata]

    async def get_commits(self):
        repos = await self.get_repos()
        log.info([repo['slug'] for repo in repos])
        log.info(f'Processing {len(repos)} repos')
        commits_by_repo = await asyncio.gather(*[self.get_commits_for_repo(repo['slug'])
                                                 for repo in repos])
        flattened = [item for commits in commits_by_repo for item in commits]

        # filter out commits without an author (these can be automatic things
        # like version bumps etc)
        flattened = [commit for commit in flattened if commit['author']]

        return [
            Commit(
                repo=commit['repo_slug'],
                timestamp=arrow.get(commit['date']).timestamp,
                hash=commit['hash'],
                author=Author(
                    name=commit['author']['user']['display_name'],
                    avatar_url=commit['author']['user']['links']['avatar']['href']
                ),
                diff=commit['diff']
            )
            for commit in flattened
        ]

    async def get_avatars(self, authors: Dict[Author, bytes]) -> dict:
        async def get_avatar(author):
            resp = await self.client.get(f"{author.avatar_url}")
            return await resp.read()

        avatars_by_author = dict(zip(
            authors,
            await asyncio.gather(*[get_avatar(author) for author in authors])
        ))

        return avatars_by_author
