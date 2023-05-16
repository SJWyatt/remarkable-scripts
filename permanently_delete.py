#!/usr/bin/python3
"""
Author: Steven Wyatt
Date: 2023-05-16
Description: This script deletes all already deleted files and folders from the reMarkable.

Usage:
    python3 permanently_delete.py [-y] [-f <folder>]
    -f, --folder: The folder to search in (Default: '~/.local/share/remarkable/xochitl')
    -y: Don't ask for confirmation, just delete everything.
"""
import argparse
import json
import sys
from pathlib import Path


if __name__ == "__main__":
    # This is the default location of the xochitl folder on the reMarkable 2
    xochitl_dir = Path.home() / '.local' / 'share' / 'remarkable' / 'xochitl'

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Permanently delete all already deleted files and folders from the reMarkable.")
    parser.add_argument("-f", "--folder", type=Path or str, required=False, 
                        default=xochitl_dir,
                        help="The folder to search in (Default: '~/.local/share/remarkable/xochitl')")
    parser.add_argument("-y", action='store_true', default=False, 
                        help="Don't ask for confirmation, just delete everything.")
    args = parser.parse_args()

    # Search For all the metadata files
    if not isinstance(args.folder, Path):
        xochitl_dir = Path(args.folder)
    else:
        xochitl_dir = args.folder
    metadata_files = xochitl_dir.glob('*.metadata')

    # Open each file and check if it's deleted already
    deleted_files = []
    for file in metadata_files:
        json_data = None
        
        try:
            # Open the file
            with file.open('r') as f_desc:
                # Read the file as a json string
                data = f_desc.read()

                # Parse the json string
                json_data = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"{file.stem}\n\tError: {e}")
            continue

        # Check if the file is deleted
        if json_data['deleted']:
            deleted_files.append((file, json_data))

    # Print the number of deleted files
    print(f"Found {len(deleted_files)} deleted files.")

    if len(deleted_files) == 0:
        print("No files to delete, exiting.")
        sys.exit()
    
    # Sort the files by the name
    deleted_files.sort(key=lambda x: x[1]['visibleName'])

    # Show the filenames of the deleted files
    print("Deleted files: ")
    for file, json_data in deleted_files:
        print(f"\t{json_data['visibleName']}")

    # Ask for confirmation
    if not args.y:
        confirmation = input("Are you sure you want to permanently delete all these files? (yes/n): ")
        if confirmation == 'yes':
            pass
        elif confirmation == 'no' or confirmation == 'n':
            print("Aborting...")
            sys.exit()
        elif confirmation.lower() == 'y' \
                or confirmation.lower() == 'yes' \
                or confirmation[0].lower() == 'y':
            # Ask for confirmation again
            confirmation = input("Please input 'yes' exactly if you want to delete the files: ")
            if confirmation != 'yes':
                print("Aborting...")
                sys.exit()


    # Delete the files
    for file, json_data in deleted_files:
        file.unlink()
        print(f"Deleted {file.stem}")