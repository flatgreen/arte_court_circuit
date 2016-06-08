# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import arte_court_circuit

setup(
    name='arte_court_circuit',
    version=arte_court_circuit.__version__,
    packages=find_packages(),
    author="flatgreen",
    author_email="flatgreen@gmail.com",
    description="Télécharge les derniers court-métrages de Arte Court-circuit",
    long_description=open('README.md').read(),
    install_requires=["beautifulsoup4", "begins", "dateparser >= 0.3.4",
                      "requests", "youtube-dl >= 2016.2.13"],
    include_package_data=True,
    url='https://github.com/flatgreen',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
    ],

    # La syntaxe est "nom-de-commande-a-creer = package.module:fonction".
    # voir begins et setuptools
    entry_points={
        'console_scripts': [
            'arte_court_circuit = arte_court_circuit.arte_court_circuit:main.start',
        ],
    },

    license="WTFPL",
)
