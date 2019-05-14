from setuptools import setup, find_packages

import copy
import sys
from pprint import pprint

def get_version():
    """
    returns version.
    """
    return '0.2.1'

def get_requirements(remove_links=True):
    """
    lists the requirements to install.
    """
    requirements = []
    try:
        with open('requirements.txt') as f:
            requirements = f.read().splitlines()
    except Exception as ex:
        raise OSError('Failed to read in requirements.txt file', ex)
    new_requirements = copy.copy(requirements)
    if remove_links:
        for requirement in requirements:
            # git repository url.
            if requirement.startswith("git+"):
                new_requirements.remove(requirement)
            # subversion repository url.
            if requirement.startswith("svn+"):
                new_requirements.remove(requirement)
            # mercurial repository url.
            if requirement.startswith("hg+"):
                new_requirements.remove(requirement)
            # editable URL
            if requirement.startswith("-e "):
                new_requirements.remove(requirement)
    return new_requirements

def get_links():
    """
    gets URL Dependency links.
    """
    links_list = get_requirements(remove_links=False)
    for link in links_list:
        keep_link = False
        already_removed = False
        # git repository url.
        if not link.startswith("git+"):
            if not link.startswith("svn+"):
                if not link.startswith("hg+"):
                    links_list.remove(link)
                    already_removed = True
                else:
                    keep_link = True
                if not keep_link and not already_removed:
                    links_list.remove(link)
                    already_removed = True
            else:
                keep_link = True
            if not keep_link and not already_removed:
                links_list.remove(link)
    return links_list

if not get_version():
    raise RuntimeError('Version is not set')

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="datacatalog",
    version=get_version(),
    author="Matthew Vaughn",
    author_email="opensource@sd2e.org",
    description="Python package implementing essential logic for SD2 Data Catalog",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/SD2E/python-datacatalog",
    package_data={'': ['*.json']},
    install_requires=get_requirements(),
    dependency_links=get_links(),
    packages=find_packages(),
    license="BSD",
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
)
