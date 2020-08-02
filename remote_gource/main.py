import arrow
import logging
import confuse
from .sources.bitbucket import BitbucketSource

logging.basicConfig()

config = confuse.Configuration('remote-gource', __name__)

bitbucket_config = config['sources']['bitbucket'].get()

bitbucket_source = BitbucketSource(
    bitbucket_config['workspace'],
    bitbucket_config['client_id'],
    bitbucket_config['client_secret'],
    {
        'date_start': arrow.get('2020-07-01')
    }
)

bitbucket_source.get_commits()
