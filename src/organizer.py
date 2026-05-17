"""
Organizer module for ARM DVD Rip Organizer.
Handles file operations, episode mapping, and folder reorganization.
"""

import shutil
from pathlib import Path
from typing import Dict, Tuple, Optional
from src.parser import FolderNameParser, EpisodeFileNameParser, EpisodeMappingAnalyzer
from src.logger import get_logger
from src.config import config


class DVDDiscOrganizer:
    """Organizes a single DVD disc (folder) of ripped episodes."""

    def __init__(self, disc_folder: Path, logger=None, config_instance=None):
        """
        Initialize organizer for a disc folder.

        Args:
            disc_folder: Path to the disc folder
            logger: Logger instance
            config_instance: Config instance for reading settings
        """
        self.disc_folder = Path(disc_folder)
        self.logger = logger or get_logger()
        self.config = config_instance or config
        self.extras_folder = self.disc_folder / "extras"

        # Parse folder name
        self.metadata = None
        self._parse_folder_name()

    def _parse_folder_name(self):
        """Parse the disc folder name to extract metadata."""
        folder_name = self.disc_folder.name

        # Try automatic parsing
        parsed = FolderNameParser.parse(folder_name)

        if parsed:
            self.metadata = parsed
            self.logger.debug(
                f"✓ Parsed folder: {folder_name} -> "
                f"Series={parsed['series_name']}, S{parsed['season']:02d}, DISC{parsed['disc_number']}"
            )
        else:
            # Interactive fallback
            self.metadata = FolderNameParser.interactive_parse(folder_name)
            self.logger.warning(
                f"⚠️  Used interactive parsing for folder: {folder_name}"
            )

    def get_metadata(self) -> Dict:
        """Get parsed metadata for this disc."""
        return self.metadata

    def _find_main_feature(self) -> Optional[Path]:
        """
        Find main feature file in disc folder (supports any video extension).

        Returns:
            Path to main feature file, or None if not found
        """
        # Try to find a file with the same name as the folder (any extension)
        folder_name = self.disc_folder.name

        for file in self.disc_folder.glob(f"{folder_name}.*"):
            if file.is_file() and file.name != folder_name:
                return file

        return None

    def collect_episodes(self) -> Dict[int, Path]:
        """
        Collect all episodes from this disc (extras + main feature).

        Handles E00 (title track):
        - If E00 exists in extras: It's the first episode
        - If E00 missing: Placement depends on MAINFEATURE_PLACEMENT setting
          - first_episode: Main feature becomes E00 (for series with full title track)
          - last_episode: Main feature becomes highest episode number (default)
        - If no extras folder: Only main feature is returned as E01

        Returns:
            Dict {episode_number: file_path}
        """
        episodes = {}
        main_feature_path = self._find_main_feature()

        # Case 1: extras folder doesn't exist
        if not self.extras_folder.exists():
            if main_feature_path:
                # Only one episode (main feature) found in disc
                episodes[1] = main_feature_path
                self.logger.info(
                    f"  ✓ No extras folder found. Using main feature as E01: {main_feature_path.name}"
                )
            else:
                self.logger.warning(
                    f"  ⚠️  No extras folder and no main feature found in: {self.disc_folder}"
                )
            return episodes

        # Case 2: extras folder exists
        extras_episodes = []
        # Search for any files (supports .mp4, .txt, etc.)
        for video_file in self.extras_folder.glob("*"):
            if not video_file.is_file():
                continue

            ep_num = EpisodeFileNameParser.extract_episode_number(video_file.name)

            if ep_num is not None:
                if EpisodeFileNameParser.validate_episode_number(ep_num):
                    extras_episodes.append(ep_num)
                    episodes[ep_num] = video_file
                    if ep_num == 0:
                        self.logger.debug(
                            f"  Found title track (E00): {video_file.name}"
                        )
                    else:
                        self.logger.debug(
                            # Das taucht auf in den Logs
                            f"  Found episode: {video_file.name} (E{ep_num:02d})"
                        )
                else:
                    self.logger.warning(
                        f"  ⚠️  Episode number out of range (0-99): {video_file.name} (E{ep_num})"
                    )
            else:
                self.logger.warning(
                    f"  ⚠️  Could not extract episode number from: {video_file.name}"
                )

        # Find missing episode (main feature)
        missing_ep = EpisodeMappingAnalyzer.find_missing_episode(extras_episodes)

        if missing_ep is not None and main_feature_path:
            max_ep = max(extras_episodes) if extras_episodes else 0

            # Check if it's a real gap (missing_ep is within the sequence) or just max+1
            # Real gap: missing_ep <= max_ep (e.g., [1,3,4] → missing_ep=2, max_ep=4)
            # E00 exists: 0 in extras_episodes
            is_real_gap = missing_ep <= max_ep
            has_e00 = 0 in extras_episodes

            if is_real_gap or has_e00:
                # Real gap found or E00 exists - use find_missing_episode result
                episodes[missing_ep] = main_feature_path
                self.logger.info(
                    f"  ✓ Main feature identified as E{missing_ep:02d}: {main_feature_path.name} → {self.disc_folder.name}"
                )
            else:
                # No real gap and no E00 - apply MAINFEATURE_PLACEMENT setting
                if self.config.mainfeature_placement == "first_episode":
                    episodes[0] = main_feature_path
                    self.logger.info(
                        # Das taucht auf in den Logs
                        f"  ✓ Main feature placed as E00 (first_episode): {main_feature_path.name}"
                    )
                else:  # last_episode (default)
                    episodes[missing_ep] = main_feature_path
                    self.logger.info(
                        f"  ✓ Main feature placed as E{missing_ep:02d} (last_episode): {main_feature_path.name}"
                    )
        elif main_feature_path:
            # No missing_ep found but main feature exists
            self.logger.info(
                f"  ℹ️  E00 not found in {self.disc_folder.name} - Title track was skipped, starting with E01"
            )
        return episodes

    def get_all_episodes_for_disc(self) -> Dict[int, Path]:
        """
        Get all episodes for this disc with complete mapping.

        Returns:
            Dict {episode_on_disc: file_path}
        """
        return self.collect_episodes()


class SeriesOrganizer:
    """Organizes all discs of a series into output directory."""

    def __init__(
        self,
        output_base: Path,
        logger=None,
        file_operation="move",
        delete_source=True,
        config_instance=None,
    ):
        """
        Initialize series organizer.

        Args:
            output_base: Base output directory
            logger: Logger instance
            file_operation: "move" or "copy"
            delete_source: Whether to delete source after move
            config_instance: Config instance for reading settings
        """
        self.output_base = Path(output_base)
        self.logger = logger or get_logger()
        self.file_operation = file_operation
        self.delete_source = delete_source
        self.config = config_instance or config

        # Collect discs by series and season
        self.disc_organizers: Dict[str, Dict[int, DVDDiscOrganizer]] = {}

    def add_disc(self, disc_folder: Path):
        """
        Add a disc folder to be organized.

        Args:
            disc_folder: Path to disc folder
        """
        organizer = DVDDiscOrganizer(disc_folder, self.logger, self.config)
        metadata = organizer.get_metadata()

        series_name = metadata["series_name"]
        season = metadata["season"]
        disc_number = metadata["disc_number"]

        # Create nested dict structure
        if series_name not in self.disc_organizers:
            self.disc_organizers[series_name] = {}

        if season not in self.disc_organizers[series_name]:
            self.disc_organizers[series_name][season] = {}

        self.disc_organizers[series_name][season][disc_number] = organizer

    def process_all(self) -> bool:
        """
        Process all added discs and reorganize files.

        Returns:
            True if all successful, False if any errors
        """
        all_success = True

        for series_name in sorted(self.disc_organizers.keys()):
            self.logger.info(f"\n{'=' * 60}")
            self.logger.info(f"Processing Series: {series_name}")
            self.logger.info(f"{'=' * 60}")

            seasons = self.disc_organizers[series_name]

            for season in sorted(seasons.keys()):
                ### Das taucht auf in den Logs
                self.logger.info(f"\n  Season {season:02d}:")

                discs = seasons[season]

                # Collect all episodes from all discs
                all_episodes: Dict[
                    Tuple[int, int], Path
                ] = {}  # (disc, local_ep) -> path

                for disc_num in sorted(discs.keys()):
                    organizer = discs[disc_num]
                    episodes = organizer.get_all_episodes_for_disc()

                    for local_ep, file_path in episodes.items():
                        all_episodes[(disc_num, local_ep)] = file_path

                # Map to final episode numbers
                disc_ep_map = {}
                for disc_num in sorted(discs.keys()):
                    organizer = discs[disc_num]
                    episodes = organizer.get_all_episodes_for_disc()
                    disc_ep_map[disc_num] = list(sorted(episodes.keys()))

                final_mapping = EpisodeMappingAnalyzer.map_episodes_to_final_numbers(
                    disc_ep_map
                )

                # Create output directory for this series/season
                season_dir = self.output_base / series_name / f"Season_{season:02d}"
                season_dir.mkdir(parents=True, exist_ok=True)

                # Move/copy files with new names
                for (disc_num, local_ep), src_file in all_episodes.items():
                    final_ep = final_mapping[(disc_num, local_ep)]

                    # Preserve the original file extension
                    file_extension = src_file.suffix
                    new_filename = (
                        f"{series_name}_S{season:02d}_E{final_ep:02d}{file_extension}"
                    )
                    dest_file = season_dir / new_filename

                    # Check if destination already exists
                    if dest_file.exists():
                        response = self._ask_file_exists(dest_file, src_file)
                        if response == "skip":
                            self.logger.warning(
                                f"    ⊘ Skipped (exists): {src_file} → {dest_file}"
                            )
                            continue
                        elif response == "overwrite":
                            dest_file.unlink()

                    # Perform file operation
                    try:
                        if self.file_operation == "move":
                            shutil.move(str(src_file), str(dest_file))
                            operation = "Moved"
                        else:  # copy
                            shutil.copy2(str(src_file), str(dest_file))
                            operation = "Copied"

                        self.logger.info(f"    ✓ {operation}: {src_file} → {dest_file}")
                    except Exception as e:
                        self.logger.error(f"    ✗ Error: {src_file} → {dest_file}: {e}")
                        all_success = False

                # Delete source disc folder if move operation
                if self.file_operation == "move" and self.delete_source:
                    for disc_num in sorted(discs.keys()):
                        organizer = discs[disc_num]
                        disc_folder = organizer.disc_folder

                        try:
                            if disc_folder.exists():
                                shutil.rmtree(disc_folder)
                                self.logger.info(
                                    f"  ✓ Deleted source folder: {disc_folder}"
                                )
                        except Exception as e:
                            self.logger.error(
                                f"  ✗ Error deleting source folder {disc_folder}: {e}"
                            )
                            all_success = False

        return all_success

    @staticmethod
    def _ask_file_exists(dest_file: Path, src_file: Path) -> str:
        """
        Ask user what to do if destination file already exists.

        Args:
            dest_file: Destination file path
            src_file: Source file path

        Returns:
            "overwrite", "skip", or "rename"
        """
        print(f"\n⚠️  File already exists: {dest_file.name}")
        print(f"  Source: {src_file}")
        print(f"  Dest:   {dest_file}")

        while True:
            response = (
                input("  Action? (o)verwrite, (s)kip, (r)ename, (a)bort: ")
                .strip()
                .lower()
            )
            if response in ["o", "overwrite"]:
                return "overwrite"
            elif response in ["s", "skip"]:
                return "skip"
            elif response in ["r", "rename"]:
                return "rename"
            elif response in ["a", "abort"]:
                raise KeyboardInterrupt("User aborted operation")
            else:
                print("  ❌ Invalid input. Please enter o, s, r, or a.")
