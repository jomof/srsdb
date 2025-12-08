from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="srsdb",
    version="0.7.0",
    author="jomof",
    author_email="",
    description="SQLite database for tracking SRS learning state with FSRS and Ebisu algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jomof/srsdb",
    project_urls={
        "Bug Reports": "https://github.com/jomof/srsdb/issues",
        "Source": "https://github.com/jomof/srsdb",
        "Documentation": "https://github.com/jomof/srsdb#readme",
    },
    py_modules=[
        "srs_database",
        "fsrs_database",
        "ebisu_database",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="srs spaced-repetition flashcards learning fsrs ebisu memory",
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for core FsrsDatabase functionality
    ],
    extras_require={
        "ebisu": [
            "ebisu>=2.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ebisu>=2.0.0",
        ],
    },
    include_package_data=False,
    zip_safe=False,
)
