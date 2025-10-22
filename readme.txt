==================================================
  File Encoding Converter (txtconv.py)
==================================================

Author: Igor Brzezek
GitHub: https://github.com/igorbrzezek
Version: 2.4

[ ABOUT THIS SCRIPT ]
---------------------
This is a command-line tool written in Python to detect and convert the encoding of text files. It was designed for batch processing and for robustly handling legacy files with non-standard character sets (like Polish diacritics in windows-1250), which are often misidentified by other tools.

The script's main strengths are its robust decoding, which uses a priority-based fallback system, and its flexible options for batch processing entire directory structures.


[ KEY FEATURES ]
----------------
* Detects the encoding of single or multiple files.
* Converts files between various formats: UTF-8 (with and without BOM), ANSI (CP-1250), ISO-8859-2, etc.
* Features a smart fallback mechanism to correctly convert Polish characters.
* Batch processes entire directories (using the --all option).
* Recursively searches through subdirectories (using the -r option).
* Displays file information without modification (using the --show option).
* Shows file statistics (size, creation date) in neatly aligned columns (--stat, --rem).
* Provides a colorized and readable console interface (--color).


[ REQUIREMENTS & INSTALLATION ]
-------------------------------
The script requires Python 3 and two external libraries.

1. Make sure you have Python 3 installed.
2. Install the required libraries using pip:

   pip install chardet colorama


==================================================
  DETAILED USAGE EXAMPLES
==================================================

[ Example 1: Basic Detection ]
------------------------------
To simply check the encoding of a single file without changing it.

> python txtconv.py -i my_document.txt

Output:
[INFO] File 'my_document.txt' detected encoding: windows-1250 (confidence 99.0%)


[ Example 2: Single File Conversion ]
-------------------------------------
To convert one file to another, specifying the input, output, and target format.

> python txtconv.py -i input_ansi.txt -o output_utf8.txt --format UTF8BOM

Output:
[INFO] Chardet detected: windows-1250 (confidence 99.0%)
[INFO] Successfully decoded using 'windows-1250'.
[OK] Saved as output_utf8.txt (UTF8BOM)


[ Example 3: Batch Conversion of a Directory ]
----------------------------------------------
To convert all `.csv` files in the `data` directory to UTF-8 without BOM. New files will be saved with a `_UTF8` suffix (e.g., `report.csv` -> `report_UTF8.csv`).

> python txtconv.py --all csv -d ./data --format UTF8WBOM --suffix UTF8 --color

Output:
Processing 5 file(s) with extension .csv in ./data
[INFO] Chardet detected: ...
[OK] Saved as file1_UTF8.csv (UTF8WBOM)
...
Batch conversion complete.


[ Example 4: Advanced Analysis (Recursive Show + Stats) ]
---------------------------------------------------------
To analyze all `.log` files in the current directory and all subdirectories. This command will display detailed stats (size, date) and align all columns neatly for maximum readability. It is the best command for auditing a project's files.

> python txtconv.py --show log -r --stat --rem --color

Output:
Directory: C:\Project\logs
  -> main.log        | utf-8 (99.0%) |   15.23 KB | 2025-10-21 10:30:00
  -> error.log       | ASCII (100%)  |    1.05 KB | 2025-10-21 10:32:15
--- Subtotal: 2 file(s), Total size: 16.28 KB ---

Directory: C:\Project\logs\archive
  -> old_log.log     | windows-1250 (89.5%) |  128.50 KB | 2024-09-15 14:00:00
--- Subtotal: 1 file(s), Total size: 128.50 KB ---

===================================================================
Grand Total: 3 file(s), Total cumulative size: 144.78 KB
===================================================================


==================================================
  DETAILED OPTIONS REFERENCE (--help output)
==================================================

Tool:     txtconv.py
Author:   Igor Brzezek
GitHub:   https://github.com/igorbrzezek
Version:  2.4
------------------------------------------------------------
Usage:
  python txtconv.py -i FILE [-o NEW] [--format FORMAT]
  python txtconv.py --all EXT --format FORMAT [--suffix NAME]
                    [-d DIR] [-r] [--color]
  python txtconv.py --show EXT [-d DIR] [-r] [--stat] [--rem] [--color]

Options:
  -i, --input FILEIN     Input file to analyze.
  -o, --output FILEOUT   Output file after conversion (optional).
  --format FORMAT        Target encoding:
                         UTF8 | UTF8WBOM | UTF8BOM | ANSI | ISO8859_2 | UTF16LE | UTF16BE
  
  --all EXT              Convert all files with given extension in directory.
  --suffix NAME          Custom suffix for new files (default = target format).
  
  --show EXT             Show encoding for all files with extension EXT.
  --stat                 Show file size/date and summaries.
  --rem                  (Requires --show) Aligns all columns for a clean output.

  -d, --dir DIR          Source directory (default = current directory).
  -r, --recursive        Search recursively through subdirectories.
  --color                Enable colorized output.
  
  -h                     Show short help and exit.
  --help                 Show this detailed help.

Requirements:
  pip install chardet colorama