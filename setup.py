
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="landsat_qa",
    version="0.1.2",
    packages=find_packages(),
    scripts=['landsat_qa.py'],
    author="AdamR",
    author_email="25871157+and-viceversa@users.noreply.github.com",
    description="Unpack Landsat-8 BQA band into individual layers and create a composite image of each quality indicator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/and-viceversa/landsat_L1_qa_tool",
    license=open('LICENSE').read(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Unlicense',
        'Topic :: Landsat :: data conversion']
)
