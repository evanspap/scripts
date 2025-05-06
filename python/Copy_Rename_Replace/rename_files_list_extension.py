import os
import csv
import sys

def rename_files_from_csv(csv_file, col_a, input_ext, col_b, output_ext, dry_run=False):
    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if col_a not in reader.fieldnames or col_b not in reader.fieldnames:
                print(f"Error: Columns '{col_a}' or '{col_b}' not found in the CSV file.")
                return

            for row in reader:
                old_name = f"{row[col_a]}{input_ext}"
                new_name = f"{row[col_b]}{output_ext}"

                if os.path.exists(old_name):
                    if dry_run:
                        print(f"[Dry-Run] Would rename '{old_name}' to '{new_name}'.")
                    else:
                        try:
                            os.rename(old_name, new_name)
                            print(f"Renamed '{old_name}' to '{new_name}'.")
                        except Exception as e:
                            print(f"Error renaming '{old_name}' to '{new_name}': {e}")
                else:
                    print(f"File '{old_name}' does not exist. Skipping.")
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) not in (6, 7):
        print("Usage: python rename_files.py <csv_file> <column_a> <input_ext> <column_b> <output_ext> [--dry-run]")
        sys.exit(1)

    csv_file = sys.argv[1]
    column_a = sys.argv[2]
    input_ext = sys.argv[3]
    column_b = sys.argv[4]
    output_ext = sys.argv[5]
    dry_run = '--dry-run' in sys.argv

    rename_files_from_csv(csv_file, column_a, input_ext, column_b, output_ext, dry_run=dry_run)
