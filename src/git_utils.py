import git
import logging

logger = logging.getLogger(__name__)
logging.getLogger('git').setLevel(logging.INFO)

def clone_git_repo(url, destination):
    logger.debug(f"Cloning repo {url}...")
    try:
        repo = git.Repo.clone_from(url, destination, branch='master')
        return repo
    except:
        pass
