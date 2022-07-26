from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="compass",
    version="2022.07.26",
    packages=find_packages(),
    install_requires=requirements,
)
