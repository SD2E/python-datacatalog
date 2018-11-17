import os
import subprocess
import git

def get_sha1_short(repo=os.getcwd()):
    """Return abbreviated SHA1 hash for the specified git repository

    Returns the initial seven characters of the current repository's most
    recent git commit.

    Args:
        repo (str, optional): The directory to inspect for a git reflog

    Returns:
        str: A hexadecimal string representing the SHA1 hash
    """
    return get_sha1(repo)[0:7]

def get_sha1(repo=os.getcwd()):
    """Get SHA-1 hash of given git repository

    Inspects the specified directory, assumed to be a git repository, and
    returns the SHA1 hash from its `HEAD-revision`. The output is equivalent to
    calling `git rev-parse HEAD`.

    Args:
        repo (str, optional): The directory to inspect for a git reflog

    Returns:
        str: A hexadecimal string representing the SHA1 hash

    Todo:
        Replace with native GitPython code
    """
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo)
    return sha.decode('ascii').strip()

def get_remote_uri(repo=os.getcwd()):
    """Gets the remote origin for the current directory

    Args:
        repo (str, optional): The directory to inspect for a git reflog

    Returns:
        str: an SSH or HTTP git repository URL

    Todo:
        Allow return of alternate forms via `giturlparse.py` or similar
    """
    repo = git.Repo(repo, search_parent_directories=True)
    return repo.remote("origin").url
