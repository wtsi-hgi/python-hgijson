from setuptools import setup, find_packages

setup(
    name="hgijson",

    version="0.5.0",

    author="Colin Nolan",
    author_email="hgi@sanger.ac.uk",

    packages=find_packages(exclude=["tests"]),

    url="https://github.com/wtsi-hgi/python-json",

    license="LICENSE.txt",

    description="Python 3 JSON Library.",
    long_description=open("README.md").read(),

    install_requires=[x for x in open("requirements.txt").read().splitlines() if "://" not in x],
    dependency_links=[x for x in open("requirements.txt").read().splitlines() if "://" in x],

    test_suite="hgijson.tests"
)
