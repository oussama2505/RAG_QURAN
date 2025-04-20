from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quran-cli",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A command-line interface for the Quran Knowledge Explorer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/quran-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=10.0.0",
        "typing-extensions>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "quran-cli=backend.cli.main:main",
        ],
    },
) 