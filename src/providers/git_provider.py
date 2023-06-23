import git
import logging

class gitProvider:
    
    def __init__(self) -> None:
        logging.getLogger('git').setLevel(logging.INFO)
        logger = logging.getLogger(__name__)
        self.logger = logger
    
    def clone_git_repo(self, url, destination):
        self.logger.debug(f"Cloning repo {url}...")
        try:
            repo = git.Repo.clone_from(url, destination, branch='master')
            return repo
        except:
            pass
