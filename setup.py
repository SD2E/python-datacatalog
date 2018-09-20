import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

requires = [pkg for pkg in open('requirements.txt').readlines()]

setuptools.setup(
    name="datacatalog",
    version="0.1.4",
    author="Matthew Vaughn",
    author_email="opensource@sd2e.org",
    description="Python package implementing essential logic for SD2 Data Catalog",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/SD2E/python-datacatalog",
    install_requires=requires,
    packages=setuptools.find_packages(),
    license="BSD",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
)
