import git

def clone_git_repo(url, destination):
    try:
        repo = git.Repo.clone_from(url, destination, branch='master')
        return repo
    except:
        pass
