import asyncio
import logging
import math
from typing import List

import aiohttp
import arrow

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def time_filter_query(filters, time_key):
    def to_iso_date(d: arrow): return d.format('YYYY-MM-DD')

    query = ''
    if "date_start" in filters:
        query += f"{time_key}>={to_iso_date(filters['date_start'])}"
    if "date_end" in filters:
        query += f"{time_key}<={to_iso_date(filters['date_end'])}"

    return query


class Pagination:
    """
    Pagination is described in detail here:

        https://developer.atlassian.com/bitbucket/api/2/reference/meta/pagination

    A noteworthy caveat in the above docs is that the 'size' (total items in
    all pages) field isn't always present in the response since it can be
    expensive to compute. In these cases, we fall back to a slower, serial
    approach.
    """

    def __init__(
        self,
        client: aiohttp.ClientSession,
        url: str,
        filters: dict = {},
        fields: List[str] = [],
        time_key=None
    ):
        self.client = client
        self.url = url

        self.params = {'pagelen': 100}
        # Bitbucket nests the actual values inside a "values" object. We want to
        # make this transparent to the caller.
        if fields:
            fields = [f'values.{f}' for f in fields]

        # Always sort the newest records first.
        if time_key:
            time_key = f'values.{time_key}'
            fields.append(time_key)
            self.params['sort'] = f'-{time_key}'
            self.params['q'] = time_filter_query(filters, time_key)

        if fields or time_key:
            self.params['fields'] = ','.join(fields)

    async def get_all(self):
        first_page = await self.get_page(1)
        if 'size' in first_page:
            log.debug('Fetching all pages in parallel')
            numPages = math.ceil(first_page['size'] / params['pagelen'])
            return first_page['values'] + await self.parallel(numPages)

        log.debug('Fetching all pages in serial')
        return first_page['values'] + await self.serial()

    async def get_page(self, pageNumber):
        resp = await self.client.get(self.url, params=dict(**self.params, page=pageNumber))
        return await resp.json()

    async def serial(self):
        """ Start from the second page, since we already have the first """
        values = []
        pageNum = 2
        page = await self.get_page(pageNum)
        while page['values']:
            values += page['values']
            pageNum += 1
            page = await self.get_page(pageNum)

        return values

    async def parallel(self, numPages):
        """ Start from the second page, since we already have the first """
        pages = await asyncio.gather(*[self.get_page(i) for i in range(2, numPages)])
        # return a flattened list
        return [item for page in pages for item in page['value']]
