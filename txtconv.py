#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text file encoding detector and converter.
Also allows showing file encodings, stats, and colorized output.

Author: Igor Brzezek
Email: igor.brzezek@gmail.com
GitHub: https://github.com/igorbrzezek
Version: 2.5
Date: 2025-10-22
"""

import argparse
import os
import sys
import glob
import math
from datetime import datetime
import colorama

# ===== Metadata =====
AUTHOR  = "Igor Brzezek"
EMAIL   = "igor.brzezek@gmail.com"
GIT     = "https://github.com/igorbrzezek"
VERSION = "2.5" # Zwiększona wersja
DATE    = "2025-10-22"

# ===== Global Definitions =====
SUPPORTED_FORMATS = {
    'UTF8': 'utf-8',
    'UTF8WBOM': 'utf-8',
    'UTF8BOM': 'utf-8-sig',
    'ANSI': 'cp1250',
    'ISO8859_2': 'iso8859_2',
    'UTF16LE': 'utf-16-le',
    'UTF16BE': 'utf-16-be'
}

# ===== chardet dependency =====
try:
    import chardet
except ImportError:
    print("ERROR: Missing required module 'chardet'. Install it with:")
    print("    pip install chardet")
    sys.exit(1)

# ===== Color support =====
class AnsiColors:
    """Helper class for aesthetic color output."""
    def __init__(self):
        self.enabled = False
        self.BLUE, self.GREEN, self.YELLOW, self.RED = "", "", "", ""
        self.CYAN, self.MAGENTA, self.GREY, self.RESET = "", "", "", ""

    def set_enabled(self, enabled):
        if enabled and sys.stdout.isatty():
            self.enabled = True
            self.BLUE, self.GREEN, self.YELLOW, self.RED = colorama.Fore.BLUE, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.RED
            self.CYAN, self.MAGENTA, self.GREY, self.RESET = colorama.Fore.CYAN, colorama.Fore.MAGENTA, colorama.Style.DIM, colorama.Style.RESET_ALL
        else:
            self.enabled = False
            self.BLUE, self.GREEN, self.YELLOW, self.RED = "", "", "", ""
            self.CYAN, self.MAGENTA, self.GREY, self.RESET = "", "", "", ""

C = AnsiColors()

# ===== Helper functions =====
def format_size(size_bytes):
    """Formats size in bytes to a human-readable string."""
    if size_bytes == 0: return "0 B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def detect_encoding(filename):
    """Detect the text file encoding for display purposes."""
    try:
        with open(filename, 'rb') as f: data = f.read()
        if not data: return 'empty', 1.0
        result = chardet.detect(data)
        return result.get('encoding', 'unknown'), result.get('confidence', 0)
    except (IOError, PermissionError) as e:
        return f"Error: {e}", 0

def convert_encoding(file_in, file_out, target_format):
    """
    Robustly converts file encoding using a priority list for Polish encodings.
    """
    target_format_upper = target_format.upper()
    
    try:
        with open(file_in, 'rb') as f:
            raw_data = f.read()
    except (IOError, PermissionError) as e:
        print(f"{C.RED}Error: Cannot read file '{file_in}': {e}{C.RESET}")
        return

    if not raw_data:
        open(file_out, 'w').close()
        print(f"{C.GREEN}[OK]{C.RESET} Created empty file {C.CYAN}{file_out}{C.RESET} ({target_format_upper})")
        return
        
    detection = chardet.detect(raw_data)
    detected_encoding = detection.get('encoding')
    confidence = detection.get('confidence')
    print(f"{C.BLUE}[INFO]{C.RESET} Chardet detected: {C.YELLOW}{detected_encoding or 'unknown'}{C.RESET} (confidence {confidence*100:.1f}%)")

    text = None
    
    # Priority list of encodings for Polish text.
    encodings_to_try = [
        'windows-1250',
        'iso8859_2',
    ]
    # Add chardet's suggestion if it's not a priority one and exists
    if detected_encoding and detected_encoding not in encodings_to_try:
        encodings_to_try.append(detected_encoding)

    # If a UTF format is detected, trust it first.
    if detected_encoding and 'utf' in detected_encoding.lower():
        try:
            text = raw_data.decode(detected_encoding)
            print(f"{C.BLUE}[INFO]{C.RESET} Successfully decoded using detected Unicode format: '{detected_encoding}'.")
        except UnicodeDecodeError:
            text = None # Mark as failed to allow fallbacks

    if text is None: # If not decoded yet (not UTF or UTF decoding failed)
        for enc in encodings_to_try:
            try:
                text = raw_data.decode(enc)
                if enc != detected_encoding:
                    print(f"{C.YELLOW}[INFO]{C.RESET} Used fallback '{enc}' for successful decoding.")
                else:
                    print(f"{C.BLUE}[INFO]{C.RESET} Successfully decoded using '{enc}'.")
                break 
            except (UnicodeDecodeError, TypeError):
                continue

    if text is None:
        print(f"{C.RED}ERROR: All decoding attempts failed. Could not correctly read the source file. Conversion aborted.{C.RESET}")
        return

    try:
        with open(file_out, 'w', encoding=SUPPORTED_FORMATS[target_format_upper], newline='') as fout:
            fout.write(text)
        print(f"{C.GREEN}[OK]{C.RESET} Saved as {C.CYAN}{file_out}{C.RESET} ({target_format_upper})")
    except Exception as e:
        print(f"{C.RED}Error writing to file {file_out}:{C.RESET} {e}")

def get_files(ext, base_dir, recursive):
    """Constructs path and gets file list based on recursive flag."""
    pattern = os.path.join(base_dir, '**', f'*.{ext}') if recursive else os.path.join(base_dir, f'*.{ext}')
    return sorted(glob.glob(pattern, recursive=recursive))

# === FUNKCJA ZMODYFIKOWANA (dodany argument 'overwrite' i logika sprawdzania) ===
def process_all(ext, target_format, suffix=None, base_dir='.', recursive=False, overwrite=False):
    """Batch process all files with given extension."""
    ext, suffix = ext.lstrip('.'), suffix or target_format.upper()
    files = get_files(ext, base_dir, recursive)
    
    if not files:
        print(f"No files found with extension .{ext} in {os.path.abspath(base_dir)}")
        return

    # --- NOWA LOGIKA SPRAWDZANIA PRZED URUCHOMIENIEM ---
    existing_files = []
    output_map = [] # Przechowuje pary (plik_in, plik_out)
    
    for fname in files:
        base, extension = os.path.splitext(fname)
        new_name = f"{base}_{suffix}{extension}"
        output_map.append((fname, new_name)) # Zapisz parę
        if os.path.exists(new_name):
            existing_files.append(new_name)

    if existing_files and not overwrite:
        print(f"{C.RED}ERROR:{C.RESET} The following {len(existing_files)} output file(s) already exist:")
        for f in existing_files:
            print(f"  - {f}")
        try:
            response = input(f"Overwrite all conflicting files and continue batch processing? [y/N]: ").strip().lower()
            if response != 'y':
                print(f"{C.YELLOW}Aborted by user. No files were converted.{C.RESET}")
                return # Zatrzymaj całą operację
        except KeyboardInterrupt:
            print(f"\n{C.YELLOW}Aborted by user (Ctrl+C). No files were converted.{C.RESET}")
            return # Zatrzymaj całą operację
    # --- KONIEC NOWEJ LOGIKI SPRAWDZANIA ---

    print(f"Processing {C.YELLOW}{len(files)}{C.RESET} file(s) with extension {C.MAGENTA}.{ext}{C.RESET} in {C.CYAN}{os.path.abspath(base_dir)}{C.RESET}")
    
    # Przetwarzaj tylko jeśli użytkownik się zgodził (lub nie było konfliktów)
    for fname_in, fname_out in output_map:
        convert_encoding(fname_in, fname_out, target_format)
        
    print("Batch conversion complete.")

def show_files_info(ext, base_dir='.', recursive=False, show_stats=False, fixed_width=False):
    """Show encoding and optionally stats for files."""
    ext = ext.lstrip('.')
    files = get_files(ext, base_dir, recursive)
    if not files:
        print(f"No files found with extension .{ext} in {os.path.abspath(base_dir)}")
        return

    files_by_dir = {}
    for f in files:
        dir_path = os.path.dirname(f) or '.'
        if dir_path not in files_by_dir: files_by_dir[dir_path] = []
        files_by_dir[dir_path].append(f)

    total_files, total_size = 0, 0
    for dir_path, dir_file_list in sorted(files_by_dir.items()):
        if recursive or (not recursive and base_dir != dir_path):
             print(f"\n{C.GREEN}Directory: {C.CYAN}{os.path.abspath(dir_path)}{C.RESET}")

        dir_data, max_widths = [], {'name': 0, 'enc': 0, 'size': 0}
        dir_files, dir_size = 0, 0

        for fname in dir_file_list:
            data = {'basename_raw': os.path.basename(fname)}
            encoding, conf = detect_encoding(fname)
            data['enc_raw'] = f"{encoding} ({conf*100:.1f}%)"
            if show_stats:
                try:
                    stats = os.stat(fname)
                    file_size = stats.st_size
                    data['size_raw'], data['date_raw'] = format_size(file_size), datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    dir_files += 1; dir_size += file_size
                    total_files += 1; total_size += file_size
                except OSError: data['error'] = "Stats not accessible"
            dir_data.append(data)
            if fixed_width:
                max_widths['name'] = max(max_widths['name'], len(data['basename_raw']))
                max_widths['enc'] = max(max_widths['enc'], len(data['enc_raw']))
                if show_stats and 'size_raw' in data: max_widths['size'] = max(max_widths['size'], len(data['size_raw']))

        for data in dir_data:
            name_pad = ' ' * (max_widths['name'] - len(data['basename_raw'])) if fixed_width else ''
            enc_pad = ' ' * (max_widths['enc'] - len(data['enc_raw'])) if fixed_width else ''
            line = f"  -> {C.CYAN}{data['basename_raw']}{C.RESET}{name_pad} | {C.YELLOW}{data['enc_raw']}{C.RESET}{enc_pad}"
            if show_stats:
                if 'error' in data: line += f" | {C.RED}{data['error']}{C.RESET}"
                else:
                    size_pad = ' ' * (max_widths['size'] - len(data['size_raw'])) if fixed_width else ''
                    line += f" | {size_pad}{C.MAGENTA}{data['size_raw']}{C.RESET} | {C.GREY}{data['date_raw']}{C.RESET}"
            print(line)

        if show_stats and dir_files > 0:
            print(f"{C.YELLOW}--- Subtotal: {dir_files} file(s), Total size: {format_size(dir_size)} ---{C.RESET}")

    if show_stats and total_files > 0:
        print(f"\n{C.BLUE}==================================================================={C.RESET}")
        print(f"{C.GREEN}Grand Total: {total_files} file(s), Total cumulative size: {format_size(total_size)}{C.RESET}")
        print(f"{C.BLUE}==================================================================={C.RESET}")


def show_detailed_help():
    """Display extended help (--help)."""
    supported_formats_str = ' | '.join(SUPPORTED_FORMATS.keys())
    print(f"""
============================================================
Tool:     utf8conv.py
Author:   {AUTHOR}
Email:    {EMAIL}
GitHub:   {GIT}
Version:  {VERSION}
Date:     {DATE}
------------------------------------------------------------
Usage:
python utf8conv.py -i FILE --format FORMAT
  python utf8conv.py -i FILE [-o NEW] [--format FORMAT]
  python utf8conv.py --all EXT --format FORMAT [--suffix NAME]
                    [-d DIR] [-r] [--color]
  python utf8conv.py --show EXT [-d DIR] [-r] [--stat] [--rem] [--color]

Options:
If only -i and --format are provided, output file will be named FILE_FORMAT.ext
  -i, --input FILEIN     Input file to analyze.
  -o, --output FILEOUT   Output file after conversion (optional).
  --format FORMAT        Target encoding (auto output name if -o not given).
    --overwrite             Overwrite output file without asking (applies to -i and --all)
                         {supported_formats_str}
  
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
============================================================
    """)

# ===== Main function =====
def main():
    colorama.init()
    parser = argparse.ArgumentParser(description="Text file encoding detector and converter.", add_help=False)
    parser.add_argument('-i', '--input', dest='input_file', help='Input file to analyze')
    parser.add_argument('-o', '--output', dest='output_file', help='Output file after conversion')
    parser.add_argument('--format', dest='format', help='Target encoding')
    parser.add_argument('--all', dest='ext', help='Convert all files with extension EXT')
    parser.add_argument('--suffix', dest='suffix', help='Custom suffix for output files')
    parser.add_argument('-d', '--dir', dest='dir', default='.', help='Source directory')
    parser.add_argument('-r', '--recursive', action='store_true', help='Search recursively')
    parser.add_argument('--show', dest='show_ext', help='Show encodings for files with extension EXT')
    parser.add_argument('--stat', action='store_true', help='Show file stats with --show')
    parser.add_argument('--rem', action='store_true', help='Align columns (with --show)')
    parser.add_argument('--color', action='store_true', help='Enable colorized output')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite output file without asking')
    parser.add_argument('-h', action='help', help='Show short help')
    parser.add_argument('--help', action='store_true', help='Show detailed help')

    args = parser.parse_args()
    C.set_enabled(args.color)

    if args.help:
        show_detailed_help()
        return
        
    if args.format and args.format.upper() not in SUPPORTED_FORMATS:
        print(f"{C.RED}ERROR: Invalid format '{args.format}'.{C.RESET}")
        print(f"Supported formats are: {', '.join(SUPPORTED_FORMATS.keys())}")
        sys.exit(1)

    if args.show_ext:
        show_files_info(args.show_ext, args.dir, args.recursive, args.stat, args.rem)
        return
    
    # === WYWOŁANIE ZMODYFIKOWANE (przekazanie 'args.overwrite') ===
    if args.ext:
        if not args.format:
            print(f"{C.RED}ERROR:{C.RESET} Using --all requires specifying --format.")
            return
        process_all(args.ext, args.format, args.suffix, args.dir, args.recursive, args.overwrite)
        return
    
    if args.input_file:
        # Przypadek 1: Podano -i, -o ORAZ --format
        if args.output_file and args.format:
            convert_encoding(args.input_file, args.output_file, args.format)
        
        # Przypadek 2: Podano -i ORAZ --format (ale BEZ -o)
        # -> Automatyczna nazwa pliku + sprawdzanie nadpisania
        elif args.format and not args.output_file:
            # Automatyczne generowanie nazwy wyjściowej jeśli nie podano -o
            base, ext = os.path.splitext(args.input_file)
            auto_output = f"{base}_{args.format.upper()}{ext}"
            if os.path.exists(auto_output) and not args.overwrite:
                try:
                    response = input(f"Output file '{auto_output}' already exists. Overwrite? [y/N]: ").strip().lower()
                    if response != 'y':
                        print(f"{C.YELLOW}Aborted by user. File not overwritten.{C.RESET}")
                        return
                except KeyboardInterrupt:
                    # Poprawiono też formatowanie nowej linii w tym miejscu
                    print(f"\n{C.YELLOW}Aborted by user (Ctrl+C). File not overwritten.{C.RESET}")
                    return
            convert_encoding(args.input_file, auto_output, args.format)

        # Przypadek 3: Podano TYLKO -i (bez --format i -o)
        # -> Pokaż wykryte kodowanie
        elif not args.output_file:
            enc, conf = detect_encoding(args.input_file)
            print(f"{C.BLUE}[INFO]{C.RESET} File '{C.CYAN}{args.input_file}{C.RESET}' detected encoding: {C.YELLOW}{enc}{C.RESET} (confidence {conf*100:.1f}%)")
        
        # Przypadek 4: Inna, niepoprawna kombinacja (np. -i oraz -o, ale bez --format)
        else:
            print(f"{C.RED}ERROR:{C.RESET} For single file conversion, you must specify -i, -o, and --format.")
        return

    print(f"{C.RED}ERROR:{C.RESET} No action specified. Use -i, --all, or --show. Use -h for help.")


if __name__ == "__main__":
    main()