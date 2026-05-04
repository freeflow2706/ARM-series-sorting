#!/usr/bin/env python3
"""
Script to create a test directory structure for the ARM organizer.
This creates realistic ARM folder structures with test files.
"""

from pathlib import Path


def create_test_structure():
    """Create complete test directory structure."""

    test_input = Path(__file__).parent / "test_input"
    # Clean up old test_input if it exists
    if test_input.exists():
        import shutil

        shutil.rmtree(test_input)
    test_input.mkdir(exist_ok=True)

    # Define test shows with their discs
    # Format: series_name, season, list of (disc_number, extras_episodes_list, has_gap)
    # has_gap: True means there's a missing episode (main feature), False means max+1 is main feature
    # episodes can include 0 for title track
    test_shows = [
        # Show 1: BIG_BANG_THEORY Season 5 - 2 Discs (standard format: SEASON_5_DISC_1)
        # Disc 1: 4 episodes (with gap at E03) -> E01, E02, E03, E04
        # Disc 2: 4 episodes (no gap)        -> E05, E06, E07, E08
        (
            "BIG_BANG_THEORY_SEASON_5_DISC_{}",
            "BIG_BANG_THEORY",
            5,
            [
                (
                    1,
                    [1, 2, 4],
                    True,
                ),  # Disc 1: episodes 1,2,4 in extras, 3 is main feature (gap)
                (
                    2,
                    [1, 2, 3],
                    False,
                ),  # Disc 2: episodes 1,2,3 in extras, 4 is main feature (no gap)
            ],
        ),
        # Show 2: BREAKING_BAD Season 4 - 3 Discs (shorthand format: S4_DISC_1)
        # Disc 1: 5 episodes (no gap)        -> E01, E02, E03, E04, E05
        # Disc 2: 4 episodes (with gap at E02) -> E06, E07, E08, E09
        # Disc 3: 3 episodes (no gap)        -> E10, E11, E12
        (
            "BREAKING_BAD_S4_DISC_{}",
            "BREAKING_BAD",
            4,
            [
                (1, [1, 2, 3, 4, 5], False),  # Disc 1: 5 episodes, no gap
                (
                    2,
                    [1, 3, 4],
                    True,
                ),  # Disc 2: episodes 1,3,4 in extras, 2 is main feature (gap)
                (
                    3,
                    [1, 2],
                    False,
                ),  # Disc 3: episodes 1,2 in extras, 3 is main feature (no gap)
            ],
        ),
        # Show 3: HOUSE Season 3 with E00 title track (format: S3D1)
        # Disc 1: 3 episodes with title track (E00, E01, E02), no gap
        # Disc 2: 4 episodes with title track (E00, E02, E03, E04), GAP at E01 - tests E00 + gap
        (
            "HOUSE_S3D{}",
            "HOUSE",
            3,
            [
                (
                    1,
                    [0, 1, 2],
                    False,
                ),  # Disc 1: E00 (title) + E01, E02 in extras, E03 is main feature
                (
                    2,
                    [0, 2, 3, 4],
                    True,
                ),  # Disc 2: E00 (title) + E02,E03,E04 in extras, E01 is main feature (GAP!)
            ],
        ),
        # Show 4: THE_OFFICE Season 2 without E00 title track (format: Season_2-D1)
        # Disc 1: 4 episodes (no E00, no gap) -> E01, E02, E03, E04, main is E05
        # Disc 2: 4 episodes (no E00, with gap) -> E01, E02, E04, main is E03
        (
            "THE_OFFICE_Season_2-D{}",
            "THE_OFFICE",
            2,
            [
                (
                    1,
                    [1, 2, 3, 4],
                    False,
                ),  # Disc 1: E01-E04 in extras, no E00, E05 is main
                (
                    2,
                    [1, 2, 4],
                    True,
                ),  # Disc 2: E01,E02,E04 in extras, no E00, E03 is main
            ],
        ),
    ]

    print("Creating test directory structure...\n")

    for folder_template, series_name, season, discs_list in test_shows:
        print(f"Series: {series_name} Season {season}")

        # Calculate episode offset for each disc
        total_episode_offset = 0
        disc_info = {}  # disc_num -> {"offset": offset, "total": total_episodes}

        for disc_num, extras_eps, has_gap in discs_list:
            total_eps_on_disc = len(extras_eps) + 1  # extras + main feature
            disc_info[disc_num] = {
                "offset": total_episode_offset,
                "total": total_eps_on_disc,
                "extras": extras_eps,
                "has_gap": has_gap,
            }
            total_episode_offset += total_eps_on_disc

        # Create folders and files for each disc
        for disc_num, extras_eps, has_gap in discs_list:
            folder_name = folder_template.format(disc_num)
            disc_folder = test_input / folder_name
            disc_folder.mkdir(exist_ok=True)
            extras_folder = disc_folder / "extras"
            extras_folder.mkdir(exist_ok=True)

            print(f"  ✓ {folder_name}")

            offset = disc_info[disc_num]["offset"]

            # Create main feature file
            main_feature_filename = f"{folder_name}.txt"

            # Check if E00 (title track) is included
            has_e00 = 0 in extras_eps

            # Determine main feature episode number
            if has_e00:
                # E00 is included, check for gaps in E01+
                sorted_extras = sorted(extras_eps)
                eps_without_e00 = [ep for ep in sorted_extras if ep > 0]

                # Find gap in E01+
                main_feature_local = None
                for i, ep_num in enumerate(eps_without_e00):
                    expected = i + 1
                    if ep_num != expected:
                        main_feature_local = expected
                        break

                # If no gap, main feature = max + 1
                if main_feature_local is None:
                    main_feature_local = max(eps_without_e00) + 1

                # With E00 shift, add +1 to global
                main_feature_global = offset + main_feature_local + 1
            elif has_gap:
                # Find the gap (excluding E00)
                sorted_extras = sorted(extras_eps)
                for i, ep_num in enumerate(sorted_extras):
                    expected = i + 1
                    if ep_num != expected:
                        main_feature_local = expected
                        break
                main_feature_global = offset + main_feature_local
            else:
                # No gap and no E00: main feature = max + 1
                main_feature_local = max(extras_eps) + 1
                main_feature_global = offset + main_feature_local
            final_main_name = (
                f"{series_name}_S{season:02d}_E{main_feature_global:02d}.txt"
            )
            main_feature_path = disc_folder / main_feature_filename
            main_feature_path.write_text(final_main_name)
            print(f"    └─ {main_feature_filename}")
            if has_e00:
                print(f"       → {final_main_name} (Main Feature placeholder)")
            else:
                print(
                    f"       → {final_main_name} (Main Feature, local E{main_feature_local:02d})"
                )

            # Create extras files
            for ep_num in sorted(extras_eps):
                if ep_num == 0:
                    # Title track
                    original_filename = f"B{disc_num}_t00.txt"
                    # If E00 exists, it gets remapped to E01 (+1 offset)
                    final_ep_num = offset + ep_num + 1
                    final_filename = (
                        f"{series_name}_S{season:02d}_E{final_ep_num:02d}.txt"
                    )
                    file_path = extras_folder / original_filename
                    file_path.write_text(final_filename)
                    print(f"    ├─ extras/{original_filename}")
                    print(f"       → {final_filename} (Title Track, local E00 → E01)")
                else:
                    original_filename = f"B{disc_num}_t{ep_num:02d}.txt"
                    # If E00 exists on this disc, all episodes get +1 offset
                    # Otherwise, episodes map directly
                    if has_e00:
                        final_ep_num = offset + ep_num + 1
                    else:
                        final_ep_num = offset + ep_num
                    final_filename = (
                        f"{series_name}_S{season:02d}_E{final_ep_num:02d}.txt"
                    )

                    file_path = extras_folder / original_filename
                    file_path.write_text(final_filename)
                    print(f"    ├─ extras/{original_filename}")
                    print(f"       → {final_filename} (local E{ep_num:02d})")

            print()

    print("✓ Test structure created successfully!")
    print(f"  Location: {test_input}")
    print("\n" + "=" * 70)
    print("Next steps:")
    print("1. Update .env with:")
    print(f"   INPUT_DIR={test_input}")
    print(f"   OUTPUT_DIR={test_input.parent / 'test_output'}")
    print("2. Run: python run.py")
    print("3. Check: test_output/ for organized files")
    print("4. Run: python verify_output.py")
    print("=" * 70)


if __name__ == "__main__":
    create_test_structure()
