import git
from loguru import logger

repo = git.Repo('.')


def update_code():
    logger.info("Updating code...")
    repo.remotes.origin.pull()
