from setuptools import setup, find_packages

def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    # Remove comments and empty lines
    lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    return lines

setup(
    name="tiktok-downloader",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "tiktok-downloader=tiktok_downloader.cli:main",
        ],
    },
    install_requires=parse_requirements("requirements.txt"),
)
