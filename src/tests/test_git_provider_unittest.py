import sys
import os
sys.path.append("..")
import providers.git_provider

def test_clone_git_repo():
    url = "https://github.com/githubtraining/hellogitworld"
    destination = "/tmp/repos/hellogitworld"
    
    git_provider = providers.git_provider.gitProvider()
    repo = git_provider.clone_git_repo(url, destination)
    files_in_repo = os.listdir(f"{destination}/.git")
    assert files_in_repo.__len__ != 0
