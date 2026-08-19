from pathlib import Path
import pandas as pd


def get_unique_categories(folder_path):
    unique_categories = set()
    path = Path(folder_path)

    # Find all .csv files in the directory
    csv_files = list(path.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in '{folder_path}'.")
        return unique_categories

    print(f"Scanning {len(csv_files)} CSV file(s)...")

    for file_path in csv_files:
        try:
            # Read only the 'Category' column to save memory
            df = pd.read_csv(file_path, usecols=["Category"])

            # Drop missing values and update our set
            categories_in_file = df["Category"].dropna().unique()
            unique_categories.update(categories_in_file)

        except ValueError:
            # This happens if 'Category' column doesn't exist in that specific CSV
            print(f"Skipping '{file_path.name}': 'Category' column not found.")
        except Exception as e:
            print(f"Error reading '{file_path.name}': {e}")

    return unique_categories


# --- How to use it ---
# Replace this with the actual path to your folder
target_folder = "./"

distinct_categories = get_unique_categories(target_folder)

print("\n--- Unique Categories Found ---")
print(distinct_categories)