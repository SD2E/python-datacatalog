from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

requires = [pkg for pkg in open('requirements.txt').readlines()]

setup(
    name="datacatalog",
    version="0.1.3",
    author="Matthew Vaughn",
    author_email="opensource@sd2e.org",
    description="Python package implementing essential logic for SD2 Data Catalog",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/SD2E/python-datacatalog",
    package_data={'*.json'},
    install_requires=requires,
    packages=find_packages(),
    license="BSD",
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
)
