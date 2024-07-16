import bittensor as bt
import subprocess
import os
import re
import codecs
from module_registrar import __version__


def update_repository():
    '''
    Check if the repository is up to date
    '''
    bt.logging.info("checking repository updates")
    try:
        subprocess.run(["git", "pull"], check=True)
    except subprocess.CalledProcessError:
        bt.logging.error("Git pull failed")
        return False

    here = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.dirname(here)
    init_file_path = os.path.join(parent_dir, '__init__.py')

    with codecs.open(init_file_path, encoding='utf-8') as init_file:
        if version_match := re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", init_file.read(), re.M
        ):
            new_version = version_match[1]
            bt.logging.success(f"current version: {__version__}, new version: {new_version}")
            if __version__ != new_version:
                try:
                    subprocess.run(["python3", "-m", "pip", "install", "-e", "."], check=True)
                    os._exit(1)
                except subprocess.CalledProcessError:
                    bt.logging.error("Pip install failed")
        else:
            bt.logging.info("No changes detected!")