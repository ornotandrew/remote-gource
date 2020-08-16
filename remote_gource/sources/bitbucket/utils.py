import asyncio
import json
import logging
import math
import os
from datetime import timedelta
from typing import TypedDict
from urllib.parse import parse_qs

import aiohttp
import arrow
from confuse import Configuration
from oauthlib.oauth2 import WebApplicationClient

from remote_gource.config import config

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class AuthToken(TypedDict):
    scopes: str
    access_token: str
    expires_in: int
    token_type: str
    state: str
    refresh_token: str
    expires_at: float


async def get_session(client_id: str, client_secret: str) -> AuthToken:
    """
    Use the Authorization Code Grant flow to get a token.

    This opens a browser tab.
    """
    refresh_token_file = os.path.join(config.config_dir(), '.refresh.token')
    base_url = 'https://bitbucket.org/site/oauth2'

    # If we have a refresh token, use that
    existing_token = None
    if os.path.isfile(refresh_token_file):
        with open(refresh_token_file) as f:
            existing_token = json.load(f)

    now = arrow.utcnow()
    if existing_token and arrow.get(existing_token['expires_at']) - now > timedelta(minutes=5):
        log.info('Found existing token')
        return existing_token

    # Otherwise, send the user to the browser flow
    redirect_uri = 'https://localhost:8888'
    client = WebApplicationClient(client_id)
    auth_url = client.prepare_request_uri(f'{base_url}/authorize', redirect_uri=redirect_uri)

    print(f'Please go to the following link, then copy the redirected URL back here.\n\n\t{auth_url}\n')
    code = client.parse_request_uri_response(input('URL: '))['code']
    token_reqest_params = parse_qs(client.prepare_request_body(code=code, redirect_uri=redirect_uri))

    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            f'{base_url}/access_token',
            headers={'Authorization': aiohttp.BasicAuth(client_id, client_secret).encode()},
            data=token_reqest_params
        )
        if resp.status != 200:
            log.error(await resp.text())
            raise Exception('Could not authenticate with the Bitbucket API')

    token: AuthToken = await resp.json()
    token['expires_at'] = now.shift(seconds=token['expires_in']).format(arrow.FORMAT_RFC3339)

    with open(refresh_token_file, 'w') as f:
        json.dump(token, f)

    return token
