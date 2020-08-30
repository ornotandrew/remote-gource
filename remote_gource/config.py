import arrow
import confuse

config = confuse.Configuration('remote-gource', __name__)


def get_config():
    as_dict = config.get()
    for key, value in as_dict['filters'].items():
        if key.startswith('date'):
            as_dict['filters'][key] = arrow.get(value)

    return as_dict
