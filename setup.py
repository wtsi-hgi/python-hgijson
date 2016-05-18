from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="hgijson",
    version="1.2.2",
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    packages=find_packages(exclude=["tests"]),
    install_requires = open("requirements.txt", "r").readline(),
    url="https://github.com/wtsi-hgi/python-json",
    license="MIT",
    description="Python 3 library for easily JSON encoding/decoding complex class-based Python models, using an "
                "arbitrarily complex mapping schema.",
    long_description=read_markdown("README.md"),
    keywords=["json", "serialization"],
    test_suite="hgijson.tests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License"
    ]
)
