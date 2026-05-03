#!/usr/bin/env python3
"""
Script to verify the output of the ARM organizer test.
Checks if files are correctly named and organized.
"""

from pathlib import Path
from collections import defaultdict


def verify_output(output_dir: Path = None):
    """
    Verify the output directory structure and file naming.

    Each test file contains the expected final filename as content.
    This script compares the actual filename with the expected (from content).
    """

    if output_dir is None:
        output_dir = Path(__file__).parent / "test_output"

    if not output_dir.exists():
        print(f"❌ Output directory not found: {output_dir}")
        print("   Run 'python run.py' first to generate the output.")
        return False

    print("=" * 70)
    print("VERIFICATION REPORT")
    print("=" * 70 + "\n")

    # Collect results
    results = {
        "total_files": 0,
        "correct_files": 0,
        "incorrect_files": 0,
        "missing_files": 0,
        "errors": [],
    }

    # Expected files mapping: original_file_content -> (series_folder, season_folder, filename)
    # We'll build this from the test_input
    test_input = Path(__file__).parent / "test_input"
    expected_files = defaultdict(list)

    if test_input.exists():
        for disc_folder in test_input.iterdir():
            if disc_folder.is_dir():
                # Check main feature
                main_feature = disc_folder / f"{disc_folder.name}.txt"
                if main_feature.exists():
                    expected_name = main_feature.read_text().strip()
                    expected_files[expected_name].append(main_feature)

                # Check extras
                extras_folder = disc_folder / "extras"
                if extras_folder.exists():
                    for mp4_file in extras_folder.glob("*.txt"):
                        expected_name = mp4_file.read_text().strip()
                        expected_files[expected_name].append(mp4_file)

    # Verify actual output
    print("Checking files in output directory:\n")

    for series_folder in sorted(output_dir.iterdir()):
        if not series_folder.is_dir():
            continue

        print(f"Series: {series_folder.name}")

        for season_folder in sorted(series_folder.iterdir()):
            if not season_folder.is_dir():
                continue

            print(f"  {season_folder.name}/")

            files_in_season = sorted(season_folder.glob("*.txt"))

            if not files_in_season:
                print(f"    ⚠️  No files found!")
                results["errors"].append(f"Empty season folder: {season_folder}")

            for file_path in files_in_season:
                results["total_files"] += 1
                filename = file_path.name
                file_content = file_path.read_text().strip()

                # Check if filename matches content (expected filename)
                if filename == file_content:
                    print(f"    ✓ {filename}")
                    results["correct_files"] += 1
                else:
                    print(f"    ✗ {filename}")
                    print(f"      Expected: {file_content}")
                    results["incorrect_files"] += 1
                    results["errors"].append(f"Mismatch: {filename} vs {file_content}")

        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files processed:  {results['total_files']}")
    print(f"Correct files:          {results['correct_files']}")
    print(f"Incorrect files:        {results['incorrect_files']}")

    if results["incorrect_files"] == 0 and results["total_files"] > 0:
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print(f"\n❌ TESTS FAILED")
        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  - {error}")
        return False


if __name__ == "__main__":
    import sys

    success = verify_output()
    sys.exit(0 if success else 1)
