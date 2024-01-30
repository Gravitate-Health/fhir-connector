import git
import logging

class gitProvider:
    
    def __init__(self) -> None:
        logging.getLogger('git').setLevel(logging.INFO)
        logger = logging.getLogger(__name__)
        self.logger = logger
    
    def clone_git_repo(self, url, destination, branch = 'mvp2'):
        self.logger.info(f"Cloning branch {branch} from repo {url}")
        try:
            repo = git.Repo.clone_from(url, destination, branch=branch)
            return repo
        except:
            pass
