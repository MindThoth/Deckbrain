#!/usr/bin/env python3
"""
Plotter File Inspector

Inspects unknown plotter files to help understand their format.
Does NOT parse files - only reports structural characteristics.

Usage:
    python scripts/inspect_plotter_file.py <path>
    python scripts/inspect_plotter_file.py samples/olex
    python scripts/inspect_plotter_file.py samples/maxsea/track.mf2
    python scripts/inspect_plotter_file.py samples/olex --extract
"""

import argparse
import hashlib
import os
import sys
import zipfile
from pathlib import Path
from typing import List, Dict, Any


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_first_bytes_hex(file_path: Path, num_bytes: int = 32) -> str:
    """Get first N bytes of file as hex string."""
    try:
        with open(file_path, "rb") as f:
            data = f.read(num_bytes)
            return data.hex(' ')
    except Exception as e:
        return f"Error reading bytes: {e}"


def guess_file_type(file_path: Path) -> str:
    """Guess if file is text or binary based on first bytes."""
    try:
        with open(file_path, "rb") as f:
            data = f.read(512)
            
        # Check for common binary signatures
        if data.startswith(b'PK\x03\x04'):
            return "ZIP archive"
        if data.startswith(b'\x1f\x8b'):
            return "GZIP compressed"
        if data.startswith(b'%PDF'):
            return "PDF document"
        if data.startswith(b'\x89PNG'):
            return "PNG image"
        if data.startswith(b'\xff\xd8\xff'):
            return "JPEG image"
        
        # Check if looks like text
        # Text-like if most bytes are printable ASCII or common whitespace
        text_chars = sum(1 for b in data if 32 <= b <= 126 or b in (9, 10, 13))
        if len(data) == 0:
            return "Empty file"
        text_ratio = text_chars / len(data)
        
        if text_ratio > 0.90:
            return "Text (likely)"
        elif text_ratio > 0.70:
            return "Text-like (mixed)"
        else:
            return "Binary"
            
    except Exception as e:
        return f"Unknown (error: {e})"


def detect_text_encoding(file_path: Path) -> str:
    """Try to detect text encoding."""
    encodings = ['utf-8', 'ascii', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)  # Try to read some content
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return "Unknown (binary?)"


def get_text_preview(file_path: Path, max_lines: int = 20) -> List[str]:
    """Get first N lines of a text file safely."""
    encoding = detect_text_encoding(file_path)
    
    if encoding == "Unknown (binary?)":
        return ["[File appears to be binary, cannot display as text]"]
    
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"... (truncated, showing first {max_lines} lines)")
                    break
                lines.append(line.rstrip('\r\n'))
            return lines
    except Exception as e:
        return [f"Error reading file as text: {e}"]


def inspect_zip_file(file_path: Path, extract: bool = False) -> Dict[str, Any]:
    """Inspect contents of a ZIP file."""
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            contents = []
            for info in zf.infolist():
                contents.append({
                    'name': info.filename,
                    'size': info.file_size,
                    'compressed_size': info.compress_size,
                    'is_dir': info.is_dir()
                })
            
            return {
                'is_zip': True,
                'num_files': len(contents),
                'contents': contents,
                'extracted': False
            }
    except zipfile.BadZipFile:
        return {'is_zip': False, 'error': 'Not a valid ZIP file'}
    except Exception as e:
        return {'is_zip': False, 'error': str(e)}


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def inspect_file(file_path: Path, extract_zips: bool = False, base_path: Path = None) -> None:
    """Inspect a single file and print detailed information."""
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return
    
    if file_path.is_dir():
        print(f"[SKIP] Skipping directory: {file_path}")
        return
    
    # Compute relative path for display
    if base_path:
        try:
            display_path = file_path.relative_to(base_path)
        except ValueError:
            display_path = file_path
    else:
        display_path = file_path
    
    print("=" * 80)
    print(f"FILE: {display_path}")
    print("=" * 80)
    
    # File size
    size = file_path.stat().st_size
    print(f"Size: {format_size(size)} ({size:,} bytes)")
    
    # SHA256
    sha256 = compute_sha256(file_path)
    print(f"SHA256: {sha256}")
    
    # File type guess
    file_type = guess_file_type(file_path)
    print(f"Type: {file_type}")
    
    # First bytes (hex)
    first_bytes = get_first_bytes_hex(file_path, 32)
    print(f"First 32 bytes (hex): {first_bytes}")
    
    # If it's a ZIP, inspect contents
    if 'ZIP' in file_type or file_path.suffix.lower() in ['.zip', '.kmz']:
        print("\nZIP Archive Contents:")
        zip_info = inspect_zip_file(file_path, extract_zips)
        
        if zip_info.get('is_zip'):
            print(f"   Total files: {zip_info['num_files']}")
            print("   Contents:")
            for item in zip_info['contents']:
                if item['is_dir']:
                    print(f"      [DIR]  {item['name']}")
                else:
                    print(f"      [FILE] {item['name']} ({format_size(item['size'])})")
        else:
            print(f"   [WARNING] {zip_info.get('error', 'Unknown error')}")
    
    # If it looks like text, show preview
    if 'Text' in file_type:
        encoding = detect_text_encoding(file_path)
        print(f"\nText Preview (encoding: {encoding}):")
        
        lines = get_text_preview(file_path, max_lines=20)
        for i, line in enumerate(lines, 1):
            if line.startswith("..."):
                print(f"\n{line}")
            else:
                print(f"   {i:3d} | {line}")
    
    print()


def inspect_directory(dir_path: Path, extract_zips: bool = False) -> None:
    """Recursively inspect all files in a directory."""
    if not dir_path.exists():
        print(f"[ERROR] Directory not found: {dir_path}")
        return
    
    if not dir_path.is_dir():
        print(f"[ERROR] Not a directory: {dir_path}")
        return
    
    # Find all files (excluding .gitkeep)
    files = [
        f for f in dir_path.rglob('*') 
        if f.is_file() and f.name != '.gitkeep'
    ]
    
    if not files:
        print(f"DIRECTORY: {dir_path}")
        print("   Status: Empty (waiting for sample plotter files)")
        return
    
    print(f"DIRECTORY: {dir_path}")
    print(f"   Found {len(files)} file(s)")
    print()
    
    for file_path in sorted(files):
        inspect_file(file_path, extract_zips, base_path=dir_path)


def main():
    parser = argparse.ArgumentParser(
        description='Inspect plotter files to understand their format (no parsing)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/inspect_plotter_file.py samples/olex
  python scripts/inspect_plotter_file.py samples/maxsea/track.mf2
  python scripts/inspect_plotter_file.py samples/olex/export.zip --extract
        """
    )
    
    parser.add_argument(
        'path',
        type=str,
        help='Path to file or directory to inspect'
    )
    
    parser.add_argument(
        '--extract',
        action='store_true',
        help='Extract and inspect ZIP archive contents (default: list only)'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"[ERROR] Path not found: {path}")
        sys.exit(1)
    
    print()
    print("DeckBrain Plotter File Inspector")
    print("=" * 80)
    print()
    
    if path.is_dir():
        inspect_directory(path, extract_zips=args.extract)
    else:
        inspect_file(path, extract_zips=args.extract)
    
    print("=" * 80)
    print("[DONE] Inspection complete")
    print()
    print("Next steps:")
    print("   1. Review the output above")
    print("   2. Update docs/research/<vendor>/README.md with findings")
    print("   3. Fill out the sample file checklist")
    print("   4. Design parser implementation based on file structure")
    print()


if __name__ == '__main__':
    main()

