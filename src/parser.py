"""
Parser module for ARM DVD Rip Organizer.
Handles parsing of folder names and episode filenames to extract metadata.
"""

import re
from pathlib import Path
from typing import Tuple, Optional, Dict, List


class FolderNameParser:
    """Parser for ARM folder names (e.g., BIG_BANG_THEORY_SEASON_5_DISC_1)."""

    # Regex patterns to extract series name, season, and disc number
    PATTERNS = [
        # Pattern 1: explicit SEASON/DISC keywords with flexible separators
        r"(.+?)[\s_-]+(SEASON|S)[\s_-]*(\d+)[\s_-]+(DISC|D)[\s_-]*(\d+)",
        # Pattern 2: without SEASON/DISC keywords (for edge cases)
        r"(.+?)[\s_-]+(\d+)[\s_-]+(\d+)$",
    ]

    @staticmethod
    def parse(folder_name: str) -> Optional[Dict[str, any]]:
        """
        Parse a folder name to extract series name, season, and disc number.

        Args:
            folder_name: The name of the folder (without path)

        Returns:
            Dict with keys: 'series_name', 'season', 'disc_number'
            Returns None if parsing fails
        """
        folder_name = folder_name.strip()

        # Try Pattern 1
        match = re.match(FolderNameParser.PATTERNS[0], folder_name, re.IGNORECASE)
        if match:
            series_name = match.group(1).strip()
            season = int(match.group(3))
            disc_number = int(match.group(5))

            return {
                "series_name": series_name,
                "season": season,
                "disc_number": disc_number,
            }

        return None

    @staticmethod
    def interactive_parse(folder_name: str) -> Dict[str, any]:
        """
        Interactively ask user to parse folder name if automatic parsing fails.

        Args:
            folder_name: The name of the folder

        Returns:
            Dict with parsed data
        """
        print(f"\n❌ Could not automatically parse folder: {folder_name}")
        print("Please enter the following information:\n")

        series_name = input("Series Name: ").strip()
        if not series_name:
            raise ValueError("Series name cannot be empty")

        while True:
            try:
                season = int(input("Season Number: ").strip())
                break
            except ValueError:
                print("  ❌ Invalid input. Please enter a number.")

        while True:
            try:
                disc_number = int(input("Disc Number: ").strip())
                break
            except ValueError:
                print("  ❌ Invalid input. Please enter a number.")

        return {
            "series_name": series_name,
            "season": season,
            "disc_number": disc_number,
        }


class EpisodeFileNameParser:
    """Parser for episode filenames (e.g., B2_t01.mp4 -> episode 01)."""

    @staticmethod
    def extract_episode_number(filename: str) -> Optional[int]:
        """
        Extract episode number from filename (last 2 chars before extension).

        Args:
            filename: The filename (e.g., B2_t01.mp4, C3_t07.mp4)

        Returns:
            Episode number as int, or None if extraction fails
        """
        # Remove extension
        name_without_ext = Path(filename).stem

        # Get last 2 characters
        if len(name_without_ext) >= 2:
            last_two = name_without_ext[-2:]

            # Try to parse as 2-digit number
            if last_two.isdigit():
                return int(last_two)

        return None

    @staticmethod
    def validate_episode_number(episode_num: int) -> bool:
        """Validate that episode number is reasonable (1-99)."""
        return 1 <= episode_num <= 99


class EpisodeMappingAnalyzer:
    """Analyzer to find missing episodes and create episode-to-final-number mappings."""

    @staticmethod
    def find_missing_episode(episode_numbers: List[int]) -> Optional[int]:
        """
        Find the missing episode number in a disc's episode list.

        Logic:
        - If sequence [1, 2, 3] (no gaps): Main feature = max + 1
        - If sequence [1, 3, 4] (gap at 2): Main feature = 2

        Args:
            episode_numbers: Sorted list of episode numbers found in extras folder

        Returns:
            The missing episode number (which is the main feature), or None if none found
        """
        if not episode_numbers:
            return None

        # Sort and remove duplicates
        unique_eps = sorted(set(episode_numbers))

        # Check for gaps in the sequence
        for i, ep in enumerate(unique_eps):
            expected = i + 1  # Should be 1, 2, 3, ...
            if ep != expected:
                return expected

        # No gap found: main feature = max + 1
        return max(unique_eps) + 1

    @staticmethod
    def map_episodes_to_final_numbers(
        disc_episode_map: Dict[int, List[int]],
    ) -> Dict[Tuple[int, int], int]:
        """
        Map (disc_number, episode_on_disc) to final_episode_number.

        Args:
            disc_episode_map: Dict {disc_number: [ep1, ep2, ep3, ...]}
                             Episodes are already sorted and complete for each disc

        Returns:
            Dict {(disc_number, episode_on_disc): final_episode_number}
            Example: {(1, 1): 1, (1, 2): 2, (2, 1): 4, (2, 2): 5}
        """
        mapping = {}
        episode_offset = 0

        # Process discs in order
        for disc_num in sorted(disc_episode_map.keys()):
            episodes_on_disc = sorted(disc_episode_map[disc_num])

            for local_ep_num in episodes_on_disc:
                final_ep_num = episode_offset + local_ep_num
                mapping[(disc_num, local_ep_num)] = final_ep_num

            # Update offset for next disc
            episode_offset += len(episodes_on_disc)

        return mapping
