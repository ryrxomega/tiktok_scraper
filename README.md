# TikTok Downloader — Architecture & Implementation Spec

This document describes a lean, single-process architecture and detailed design for a command-line tool to download TikTok videos and their metadata based on user-defined filters.

## 1) System architecture overview

### 1.1 Components and boundaries

- **Single CLI Application:** A Python script provides the user interface and orchestrates the entire process.
- **Core Services:**
  - **Filter & Policy Engine:** Applies user-defined filters (likes, views, etc.).
  - **Downloader Service:** Interfaces with the `yt-dlp` library.
  - **Configuration Manager:** Loads settings from a `config.ini` file.
- **External Dependencies:**
  - **TikTok:** The source of all data.
  - **yt-dlp:** The library used for all interactions with TikTok.

Mermaid component diagram:
```mermaid
graph TB
    subgraph External
        TikTok
        YTDLP[yt-dlp library]
    end

    subgraph App[CLI Application]
        CLI[Command-Line Interface]

        subgraph Core Services
            Filter[Filter & Policy Engine]
            Downloader[Downloader Service]
            Config[Configuration Manager]
        end
    end

    CLI --> Config
    CLI --> Filter
    CLI --> Downloader

    Downloader --> YTDLP
    YTDLP --- TikTok
```

### 1.2 Principles

- **Simplicity:** A single script with minimal moving parts.
- **User-centric:** A clear CLI with sensible defaults and powerful filtering options.
- **Maintainability:** A modular design that separates concerns.

## 2) Core Workflows

### 2.1 Video Fetching and Downloading

```mermaid
sequenceDiagram
  participant User
  participant CLI
  participant Config
  participant Filter
  participant Downloader
  participant YTDLP

  User->>CLI: Executes command with URL and filters
  CLI->>Config: Load config.ini
  Config-->>CLI: Default settings
  CLI->>Downloader: Initiate download process with merged settings
  Downloader->>YTDLP: Set up options (filters, output path)
  Downloader->>YTDLP: Request video metadata for URL
  YTDLP-->>Downloader: List of video metadata
  Downloader->>Filter: Apply filters to metadata
  Filter-->>Downloader: Filtered list of videos
  loop For each filtered video
    Downloader->>YTDLP: Download video and transcript
    YTDLP-->>Downloader: Files saved to disk
  end
```

## 3) CLI & API

### 3.1 CLI Stack

- **click:** For a clean, composable command-line interface.

### 3.2 CLI Commands

The script is controlled via the `tiktok-downloader` command.

**Usage:**
```
Usage: tiktok-downloader [OPTIONS] [TIKTOK_URL]
```

**Arguments:**
- `TIKTOK_URL`: The URL of the TikTok user, hashtag, or video. Optional if `--from-file` is used.

**Options:**
- `--from-file FILE`: Path to a text file containing one TikTok URL per line.
- `--output-path DIRECTORY`: Specify the download directory.
- `--min-likes INTEGER`: Filter videos with at least this many likes.
- `--min-views INTEGER`: Filter videos with at least this many views.
- `--transcripts / --no-transcripts`: Enable or disable transcript downloads.
- `--metadata-only`: Fetch and display metadata without downloading videos.

### 3.3 Library Usage

In addition to the CLI, you can use `tiktok-downloader` as a library in your own Python projects. The core functionality is exposed through the `download_videos` function.

**Example:**
```python
from tiktok_downloader import download_videos

# Download videos from a specific user, with filters
filtered_videos = download_videos(
    tiktok_url="https://www.tiktok.com/@nasa",
    output_path="nasa_videos",
    min_likes=100000,
    min_views=1000000,
    download_transcripts=True,
)

print(f"Downloaded {len(filtered_videos)} videos.")

# Alternatively, just fetch metadata without downloading
metadata = download_videos(
    tiktok_url="https://www.tiktok.com/@nasa",
    metadata_only=True,
)

for video in metadata:
    print(f"Title: {video.title}, Likes: {video.like_count}")

```

## 4) Configuration

The script can be configured via a `config.ini` file in the project's root directory.

**Example `config.ini`:**
```ini
[defaults]
output_path = ~/TikTok_Downloads
min_likes = 10000
min_views = 100000
transcripts = true
```

## 5) Deployment

### 5.1 Prerequisites

- Python 3.7+
- `pip`

### 5.2 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/tiktok-downloader.git
    cd tiktok-downloader
    ```
2.  **Install:**
    ```bash
    pip install -e .
    ```
3.  **Verify:**
    ```bash
    tiktok-downloader --version
    ```

## 6) Testing

This project uses `pytest` for testing. To run the tests, first install the development dependencies:
```bash
pip install -r requirements-dev.txt
```

Then run `pytest`:
```bash
pytest
```

### Property-Based Testing with Hypothesis

This project uses `hypothesis` for property-based testing. This allows for more robust testing by generating a wide range of test cases automatically.

### Fuzz Testing with HypoFuzz

This project is set up to use `hypofuzz` for fuzz testing. HypoFuzz is a powerful tool that can find bugs by running tests with a wide range of inputs.

To run the fuzzer, use the following command:
```bash
hypothesis fuzz
```

This will start the fuzzer, which will run indefinitely. You can stop it with `Ctrl+C`.

**Note:** The HypoFuzz dashboard might not work correctly in all environments. If you encounter issues with the dashboard, you can run the fuzzer without it using the `--no-dashboard` flag:
```bash
hypothesis fuzz --no-dashboard
```
