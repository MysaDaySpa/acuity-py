from setuptools import setup, find_packages

# Read requirements.txt
req_file = open("requirements.txt", 'r')
requirements = list(map(lambda l: l.strip(), req_file.readlines()))
req_file.close()

setup(
    name="acuity-py",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
)
