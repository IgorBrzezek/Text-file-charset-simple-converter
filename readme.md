# txtconv.py - Encoding Detector & Converter

**Version:** 2.5  
**Author:** Igor Brzezek ([https://github.com/igorbrzezek](https://github.com/igorbrzezek))

A command-line utility to detect and convert text file encodings. It is particularly useful for standardizing legacy files (e.g., ANSI, ISO-8859-2, CP-1250) to UTF-8.

The script can operate on a single file or in batch mode, processing all files with a specific extension in a directory, including subdirectories.

## Features

* **Encoding Detection:** Reliably detects the encoding of a file using `chardet`.
* **File Conversion:** Converts files to various UTF and legacy formats.
* **Batch Processing:** Convert all `*.html` (or any other extension) files in a directory at once.
* **Recursive Mode:** Use the `-r` flag to process files in subdirectories.
* **Overwrite Protection:** Asks before overwriting existing files in both single-file and batch modes. Use `--overwrite` to force.
* **Automatic Naming:** If no output (`-o`) file is specified, one is created automatically (e.g., `file_UTF8BOM.txt`).
* **Info Mode:** List encodings, file sizes, and dates for all files matching a pattern using `--show`.
* **Colorized Output:** Provides easy-to-read, color-coded terminal feedback.

## Requirements

The script requires two Python packages: `chardet` and `colorama`.

You can install them using `pip`:
```bash
pip install chardet colorama