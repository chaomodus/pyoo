"""Module setup."""

import os.path
from setuptools import setup, find_packages

PACKAGE_NAME = "pyoo"
VERSION = "0.0.3"

srcpath = os.path.dirname(__file__)

if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        packages=find_packages(),
        python_requires=">=3.6.3",
        # scripts=["scripts/adventure.py"]
        description="A simple LambdaMOO-like command interpreter for Python",
        long_description=open(os.path.join(srcpath, "README.md"), "r").read(),
        long_description_content_type="text/markdown",
    )
