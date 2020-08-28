import subprocess
import tempfile
import logging

log = logging.getLogger(__name__)


def gource(custom_log, avatars_by_author, args):
    with tempfile.TemporaryDirectory() as user_image_dir:
        for author, avatar in avatars_by_author.items():
            with open(f'{user_image_dir}/{author.name}.png', 'wb') as image_file:
                image_file.write(avatar)
            with open(f'/Users/andrew/scratch/avatars/{author.name}.png', 'wb') as image_file:
                image_file.write(avatar)

        with tempfile.NamedTemporaryFile() as log_file:
            log_file.write(custom_log.encode())
            with open(f'/Users/andrew/scratch/gource.log', 'w') as log_file_2:
                log_file_2.write(custom_log)
            # subprocess.run([
            #     'gource',
            #     '--path', log_file.name,
            #     '--user-image-dir', user_image_dir,
            #     '--viewport', '1280x720'
            # ], check=True)
