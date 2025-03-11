from setuptools import setup, find_packages

setup(
    name='xd', 
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'doc-gen=doc_gen.cli.cli:doc_gen', 
        ],
    },
)