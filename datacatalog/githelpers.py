import os
import subprocess
import git

def get_sha1_short(repo=os.getcwd()):
    return get_sha1(repo)[0:7]

def get_sha1(repo=os.getcwd()):
    """
    Grabs the current SHA-1 hash of the given directory's git HEAD-revision.
    The output of this is equivalent to calling git rev-parse HEAD.

    Be aware that a missing git repository will make this return an error message,
    which is not a valid hash.
    """
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo)
    return sha.decode('ascii').strip()

def get_remote_uri():
    repo = git.Repo(".", search_parent_directories=True)
    return repo.remote("origin").url
