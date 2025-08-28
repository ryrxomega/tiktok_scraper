from setuptools import setup, find_packages

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
    install_requires=[
        "click",
        "yt-dlp",
        "pydantic",
    ],
)
