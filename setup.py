from setuptools import setup, find_packages

setup(
    name="musiCLI",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2023.07.06",
        "psutil>=5.9.0",
        "prompt_toolkit>=3.0.0",
        "setuptools>=82.0.0",
    ],
    author="Loan34k",
    description="A simple CLI written in Python to listen music from Youtube.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "musiCLI=musique_cli.cli:main",
        ],
    },
    python_requires=">=3.8",
)
