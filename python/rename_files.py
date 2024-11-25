import os
import sys

def rename_files(extension, old_str, new_str, dry_run=False):
    """
    Renames files in the current directory based on the given extension and replacement strings.

    :param extension: The file extension to search for.
    :param old_str: The string to replace in the filename.
    :param new_str: The replacement string.
    :param dry_run: If True, only prints what would happen without renaming.
    """
    # Get the current working directory
    current_directory = os.getcwd()

    for filename in os.listdir(current_directory):
        # Check if the file ends with the specified extension
        if filename.endswith(extension):
            # Check if the file contains the string to replace
            if old_str in filename:
                # Create the new filename
                new_filename = filename.replace(old_str, new_str)

                # Print the intended operation
                if dry_run:
                    print(f'[DRY-RUN] Would rename: {filename} -> {new_filename}')
                else:
                    # Perform the rename
                    os.rename(filename, new_filename)
                    print(f'Renamed: {filename} -> {new_filename}')

if __name__ == "__main__":
    # Check for correct number of arguments
    if len(sys.argv) < 4:
        print("Usage: python rename_files.py <extension> <old_str> <new_str> [--dry-run]")
        sys.exit(1)

    # Parse arguments
    extension = sys.argv[1]
    old_str = sys.argv[2]
    new_str = sys.argv[3]
    dry_run = '--dry-run' in sys.argv

    # Call the rename function
    rename_files(extension, old_str, new_str, dry_run)
