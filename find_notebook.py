#!/usr/bin/python3
from pathlib import Path
import json
import argparse
from datetime import datetime


if __name__ == "__main__":
    # This is the default location of the xochitl folder on the reMarkable 2
    xochitl_dir = Path.home() / '.local' / 'share' / 'remarkable' / 'xochitl'

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Search for a remarkable notebook file by name. \n Note: I have only tested this with rm lines v5 files. \n Though that's not to say that it won't work with other versions.")
    parser.add_argument("-n", "--notebook_name", type=str, required=True, 
                        help="The name of the notebook to find")
    parser.add_argument("-f", "--folder", type=Path or str, required=False, 
                        default=xochitl_dir,
                        help="The folder to search in (Default: '~/.local/share/remarkable/xochitl')")
    parser.add_argument("-d", "--deleted", action='store_true', 
                        default=False, 
                        help="Whether to search for deleted notebooks as well. (Default: False)")
    parser.add_argument("-e", "--exact", action='store_true',
                        default=False,
                        help="Whether to search for an exact notebook name match. (Default: False)")
    parser.add_argument("-x", "--extra", action='store_true',
                        default=False,
                        help="Whether to print additional information about each notebook. (Default: False)")
    args = parser.parse_args()

    if args.exact:
        print(f"Searching for notebook named '{args.notebook_name}'...")
    else:
        print(f"Searching for notebook containing '{str(args.notebook_name).lower()}'...")

    # Search For all the metadata files
    if not isinstance(args.folder, Path):
        xochitl_dir = Path(args.folder)
    else:
        xochitl_dir = args.folder
    metadata_files = xochitl_dir.glob('*.metadata')

    # Open each file and search for the notebook name
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
            print(f"{file.name}\n\tError: {e}")
            continue

        # Check if the notebook name is in the json data
        if json_data is not None and str(json_data['visibleName']).lower().find(str(args.notebook_name).lower()) != -1:
            if args.exact and str(json_data['visibleName']) != str(args.notebook_name):
                # Not an exact match
                continue

            # Check that this is a document (not a directory)
            elif json_data['type'] != 'DocumentType':
                continue
            
            # Check that it hasn't been deleted
            elif not args.deleted and json_data['deleted']:
                continue

            # Print the file name
            print(f"Name: '{json_data['visibleName']}'")

            # Print the file UUID
            print(f"\tUUID: '{file.stem}'")

            # Print the file path
            print(f"\tSystem Path: {file.with_suffix('')}*")

            # Find the remarkable path
            parent = json_data['parent']
            parent_path = Path(json_data['visibleName'])
            while str(parent) != '':
                # Open the parent file
                with Path(xochitl_dir / f"{parent}.metadata").open('r') as f_desc:
                    # Read the file as a json string
                    data = f_desc.read()

                    # Parse the json string
                    parent_data = json.loads(data)

                parent = parent_data['parent']
                parent_path = Path(parent_data['visibleName']) / parent_path

                # Print the parent name
            print(f"\tRemarkable Path: {parent_path}")

            if args.deleted and json_data['deleted']:
                print("\tViewing Deleted File")

            if args.extra:
                # Print the last modified date
                try:
                    last_modified = datetime.fromtimestamp(int(json_data['lastModified'])/1000)
                    print(f"\tLast Modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
                except (KeyError, TypeError, AttributeError):
                    # Silently fail...
                    pass

                # Print the last opened info
                try:
                    last_opened_page = int(json_data['lastOpenedPage'])
                    last_opened = datetime.fromtimestamp(int(json_data['lastOpened'])/1000)
                    print(f"\tLast Opened: {last_opened.strftime('%Y-%m-%d %H:%M:%S')}")
                except (KeyError, TypeError, AttributeError):
                    # Silently fail...
                    pass

                try:
                    # Load the content metadata
                    with file.with_suffix('.content').open('r') as f_desc:
                        # Read the file as a json string
                        data = f_desc.read()

                        # Parse the json string
                        content_data = json.loads(data)

                    # Print the number of pages
                    if content_data.get('pageCount') is not None:
                        print(f"\tNum Pages: {content_data['pageCount']}")

                    if content_data.get('fileType') is not None:
                        print(f"\tFile Type: {content_data['fileType']}")

                    # Print the page size
                    if content_data.get('sizeInBytes') is not None:
                        try:
                            notebook_size = int(content_data['sizeInBytes'])
                            if notebook_size > 1024**3:
                                print(f"\tSize: {notebook_size/(1024**3):.2f} GB")
                            elif notebook_size > 1024**2:
                                print(f"\tSize: {notebook_size/(1024**2):.2f} MB")
                            elif notebook_size > 1024:
                                print(f"\tSize: {notebook_size/1024:.2f} KB")
                            else:
                                print(f"\tSize: {notebook_size} B")
                        except (TypeError, AttributeError, ValueError):
                            # Silently fail...
                            pass

                except (FileNotFoundError, json.JSONDecodeError) as e:
                    # Silently fail...
                    pass
