import sys
from setuptools import setup, find_packages

setup(
    name="evopminer",
    version="2.0.0",
    packages=find_packages(),
    author="Tommy Carpenter",
    author_email="tcarpent@uwaterloo.ca",
    description="package for mining and classifying the sentiments in EV ownership forums.",
    license="",
    keywords="",
    url="www.tommyjcarpenter.com",
    #install_requires=required,
    zip_safe=False,
    include_package_data=True
)
