"""
Main entry point for ARM DVD Rip Organizer.
Orchestrates the scanning, parsing, and reorganization of DVD rip folders.
"""

import sys
from src.config import config
from src.logger import get_logger
from src.organizer import SeriesOrganizer


def main():
    """Main function."""

    # Initialize logger
    logger = get_logger(log_level=config.log_level, log_dir=config.output_dir / "logs")

    logger.info("=" * 70)
    logger.info("ARM DVD Rip Reorganizer - Starting")
    logger.info("=" * 70)
    logger.info(f"\nConfiguration:\n{config}\n")

    # Validate input directory
    if not config.input_dir.exists():
        logger.error(f"❌ INPUT_DIR does not exist: {config.input_dir}")
        logger.error("Please create the directory or update INPUT_DIR in .env")
        return 1

    # Find all disc folders in input directory
    disc_folders = [folder for folder in config.input_dir.iterdir() if folder.is_dir()]

    if not disc_folders:
        logger.warning(f"⚠️  No folders found in INPUT_DIR: {config.input_dir}")
        logger.info(
            "Place your disc folders (e.g., BIG_BANG_THEORY_SEASON_5_DISC_1) in INPUT_DIR"
        )
        return 0

    logger.info(f"Found {len(disc_folders)} disc folders to process\n")

    # Create series organizer
    organizer = SeriesOrganizer(
        output_base=config.output_dir,
        logger=logger,
        file_operation=config.file_operation,
        delete_source=config.delete_source_after_move,
        config_instance=config,
    )

    # Add each disc folder
    for disc_folder in sorted(disc_folders):
        try:
            logger.debug(f"Adding folder: {disc_folder.name}")
            organizer.add_disc(disc_folder)
        except Exception as e:
            logger.error(f"✗ Error adding folder {disc_folder.name}: {e}")

    # Process all discs
    logger.info("\n" + "=" * 70)
    logger.info("Starting reorganization...")
    logger.info("=" * 70 + "\n")

    try:
        success = organizer.process_all()

        if success:
            logger.info("\n" + "=" * 70)
            logger.info("✓ All files processed successfully!")
            logger.info(f"Output directory: {config.output_dir}")
            logger.info("=" * 70)
            return 0
        else:
            logger.warning("\n" + "=" * 70)
            logger.warning("⚠️  Process completed with errors (see above)")
            logger.warning("=" * 70)
            return 1

    except KeyboardInterrupt:
        logger.error("\n❌ Process interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        logger.error("See log file for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
