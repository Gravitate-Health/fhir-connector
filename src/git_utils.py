import git
import logging

def clone_git_repo(url, destination):
    logging.debug(f"Cloning repo {url}...")
    try:
        repo = git.Repo.clone_from(url, destination, branch='master')
        return repo
    except:
        pass
