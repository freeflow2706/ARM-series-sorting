#!/usr/bin/env python3
"""
Script to create a mock test directory structure.
Recreates the structure of an existing directory as empty .txt files.

This is useful for testing without needing actual large media files.

Usage:
    python create_mock_structure.py <input_dir> <output_dir>
    
Example:
    python create_mock_structure.py "../test/test_input copy" "../test/test_mock_structure"
"""

import sys
from pathlib import Path
import shutil


def create_mock_structure(source_dir: Path, target_dir: Path, verbose: bool = True) -> None:
    """
    Recreate directory structure from source as empty .txt files in target.
    
    Args:
        source_dir: Source directory to analyze
        target_dir: Target directory to create mock structure in
        verbose: Print progress information
    """
    
    source_dir = Path(source_dir).resolve()
    target_dir = Path(target_dir).resolve()
    
    # Validate source directory
    if not source_dir.exists():
        print(f"❌ Source directory does not exist: {source_dir}")
        sys.exit(1)
    
    if not source_dir.is_dir():
        print(f"❌ Source path is not a directory: {source_dir}")
        sys.exit(1)
    
    # Clean up target directory if it exists
    if target_dir.exists():
        if verbose:
            print(f"🗑️  Removing existing target directory: {target_dir}")
        shutil.rmtree(target_dir)
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print(f"📁 Source: {source_dir}")
        print(f"📁 Target: {target_dir}")
        print("=" * 70)
    
    file_count = 0
    folder_count = 0
    
    # Walk through source directory
    for source_path in source_dir.rglob("*"):
        # Calculate relative path
        rel_path = source_path.relative_to(source_dir)
        target_path = target_dir / rel_path
        
        if source_path.is_dir():
            # Create directory
            target_path.mkdir(parents=True, exist_ok=True)
            folder_count += 1
            if verbose:
                print(f"✓ Folder: {rel_path}")
        
        else:
            # Create file as .txt
            # Replace extension with .txt (or add .txt if no extension)
            target_file = target_path.parent / (target_path.stem + ".txt")
            
            # Create parent directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create empty .txt file
            target_file.touch()
            file_count += 1
            if verbose:
                print(f"✓ File:   {rel_path} → {target_file.name}")
    
    print("=" * 70)
    print(f"✓ Mock structure created successfully!")
    print(f"  📊 Folders created: {folder_count}")
    print(f"  📄 Files created:   {file_count}")
    print(f"  📁 Location:        {target_dir}")


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print(__doc__)
        print("Error: Missing required arguments")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    target_dir = sys.argv[2]
    
    try:
        create_mock_structure(source_dir, target_dir, verbose=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
