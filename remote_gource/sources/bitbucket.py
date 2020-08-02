import arrow
import math
import logging
from confuse import Configuration
from requests_oauthlib import OAuth2Session
from .remote_source import AbstractRemoteSource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def get_session(client_id: str, client_secret: str) -> OAuth2Session:
    """
    Use the Authorization Code Grant flow to get a token.

    This opens a browser tab.
    """
    base_url = 'https://bitbucket.org/site/oauth2'
    session = OAuth2Session(client_id, redirect_uri='https://localhost:8888')
    auth_url, state = session.authorization_url(f'{base_url}/authorize')

    print(f'Please go to the following link, then copy the redirected URL back here.\n\n\t{auth_url}\n')
    session.fetch_token(
        f'{base_url}/access_token',
        authorization_response=input('URL: '),
        client_secret=client_secret
    )

    return session


class BitbucketSource(AbstractRemoteSource):
    """
    Unfortunately, there doesn't seem to be a python client library for Bitbucket which

    - is not abandoned
    - supports the v2 api

    So this class calls the API manually. Docs are available here:

        https://developer.atlassian.com/bitbucket/api/2/reference/resource/
    """

    def __init__(self, workspace: str, client_id: str, client_secret: str, filters: dict = {}):
        self.base_url = f'https://api.bitbucket.org/2.0/repositories/{workspace}'
        self.filters = filters
        self.client = get_session(client_id, client_secret)

    def _time_filter_query(self, time_key):
        def to_iso_date(d: arrow): return d.format('YYYY-MM-DD')

        query = ''
        if "date_start" in self.filters:
            query += f"{time_key}>={to_iso_date(self.filters['date_start'])}"
        if "date_end" in self.filters:
            query += f"{time_key}<={to_iso_date(self.filters['date_end'])}"

        return query

    def _get_all_pages(self, url, fields=[], time_key=None):
        params = {'pagelen': 100}
        if fields or time_key:
            params['fields'] = [f'values.{f}' for f in fields] + [time_key]
            if time_key:
                params['sort'] = f'-values.{time_key}'
                params['q'] = self._time_filter_query(time_key)

        def get_page(pageNumber):
            return self.client.get(url, params=dict(**params, page=pageNumber)).json()

        values = []
        pageNum = 1
        page = get_page(pageNum)
        while page['values']:
            values += page['values']
            pageNum += 1
            page = get_page(pageNum)

        return values

    def get_repos(self):
        log.info("Listing repos...")
        repos = self._get_all_pages(f'{self.base_url}', ['slug', 'updated_on'])
        # the api doesn't support filtering by 'updated_on', so we do that ourselves
        if 'date_start' in self.filters:
            repos = [r for r in repos if arrow.get(r['updated_on']).date() >= self.filters['date_start'].date()]
        if 'date_end' in self.filters:
            repos = [r for r in repos if arrow.get(r['updated_on']).date() <= self.filters['date_end'].date()]

        return repos

    def get_commits_for_repo(self, repo_slug):
        return self._get_all_pages(
            f'{self.base_url}/{repo_slug}/commits'
            ['hash', 'date', 'author.user.display_name', 'author.user.nickname', 'author.user.links.avatar.href']
        )

    def get_diff_for_commit(self, repo_slug, commit_hash):
        return self.client.get(f'{self.base_url}/{repo_slug}/diff/{commit_hash}').text

    def get_commits(self):
        repos = self.get_repos()

        print(repos)
