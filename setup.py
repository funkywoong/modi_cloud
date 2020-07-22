from os import path
from io import open
from setuptools import setup, find_packages


def get_readme():
    here = path.dirname(__file__)
    with open(path.join(here, 'README.md'),
              encoding='utf8') as readme_file:
        readme = readme_file.read()
        return readme


def get_requirements():
    here = path.dirname(__file__)
    with open(path.join(here, 'requirements.txt'),
              encoding='utf8') as requirements_file:
        requirements = requirements_file.read().splitlines()
        return requirements


setup(
    name='modi_cloud',
    version='0.1.0',
    author='funkywoong',
    author_email='tech@luxrobo.com',
    description='Networking logic for learning '
                'user code come from MODI AI modules',
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    install_requires=get_requirements(),
    include_package_data=True,
    keywords=["python", "modi", "cloud"],
    packages=find_packages(include=['modi_cloud', 'modi_cloud.util', 'modi_cloud.example',
                                    'modi_cloud.example.test']),
    test_suite="tests",
    url='https://github.com/funkywoong/modi_cloud',
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
