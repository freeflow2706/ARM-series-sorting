"""
Configuration module for ARM DVD Rip Organizer.
Loads environment variables from .env file and provides global configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration class for the ARM organizer."""

    def __init__(self):
        """Initialize configuration by loading .env file."""
        # Load .env file from parent directory of this script
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)

        # Load configuration from environment variables
        self.input_dir = Path(os.getenv("INPUT_DIR", ""))
        self.output_dir = Path(os.getenv("OUTPUT_DIR", ""))
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.file_operation = os.getenv("FILE_OPERATION", "move").lower()
        self.delete_source_after_move = (
            os.getenv("DELETE_SOURCE_AFTER_MOVE", "True").lower() == "true"
        )
        self.mainfeature_placement = os.getenv(
            "MAINFEATURE_PLACEMENT", "last_episode"
        ).lower()

        # Validate configuration
        self._validate()

    def _validate(self):
        """Validate that all required configurations are set."""
        if not self.input_dir or str(self.input_dir) == ".":
            raise ValueError(
                f"INPUT_DIR not set in .env file or invalid: {self.input_dir}"
            )

        if not self.output_dir or str(self.output_dir) == ".":
            raise ValueError(
                f"OUTPUT_DIR not set in .env file or invalid: {self.output_dir}"
            )

        if self.file_operation not in ["move", "copy"]:
            raise ValueError(
                f"FILE_OPERATION must be 'move' or 'copy', got: {self.file_operation}"
            )

        if self.mainfeature_placement not in ["first_episode", "last_episode"]:
            raise ValueError(
                f"MAINFEATURE_PLACEMENT must be 'first_episode' or 'last_episode', got: {self.mainfeature_placement}"
            )

        # Create input directory if it doesn't exist (warn user)
        if not self.input_dir.exists():
            print(f"⚠️  Warning: INPUT_DIR does not exist: {self.input_dir}")
            print(f"    Please create it or update INPUT_DIR in .env")

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def __repr__(self):
        return (
            f"Config(\n"
            f"  INPUT_DIR={self.input_dir},\n"
            f"  OUTPUT_DIR={self.output_dir},\n"
            f"  LOG_LEVEL={self.log_level},\n"
            f"  FILE_OPERATION={self.file_operation},\n"
            f"  DELETE_SOURCE_AFTER_MOVE={self.delete_source_after_move},\n"
            f"  MAINFEATURE_PLACEMENT={self.mainfeature_placement}\n"
            f")"
        )


# Global config instance
try:
    config = Config()
except ValueError as e:
    raise SystemExit(f"Configuration Error: {e}")
