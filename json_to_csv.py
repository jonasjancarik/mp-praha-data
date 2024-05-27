import os
import pandas as pd
import requests

# Load the JSON data
print("Downloading data from the server...")
data = requests.get("https://mppraha.info/opendata/cinnost/2024OR.json").json()
print("Data downloaded successfully...")

print("Converting data...")

# Flatten the JSON structure and convert it to a DataFrame
flattened_data = []
for period, districts in data.items():
    for district, categories in districts.items():
        for category, details in categories.items():
            if isinstance(details, dict):
                for subcategory, values in details.items():
                    if isinstance(values, dict):
                        for subsubcategory, count in values.items():
                            flattened_data.append(
                                [
                                    period,
                                    district,
                                    category,
                                    subcategory,
                                    subsubcategory,
                                    count,
                                ]
                            )
                    else:
                        flattened_data.append(
                            [period, district, category, subcategory, None, values]
                        )
            else:
                flattened_data.append([period, district, category, None, None, details])

# Define column names based on the structure
columns = ["období", "obvod", "typ dat", "kategorie", "přestupek", "počet"]

# Convert the flattened data to a DataFrame
df = pd.DataFrame(flattened_data, columns=columns)

# Handle the special case for 'Uložené pokuty v Kč' type
# Extract rows related to 'Uložené pokuty v Kč' to handle them separately
penalty_rows = df[df["typ dat"] == "Uložené pokuty v Kč"].copy()

# Rename the 'počet' column to 'částka' for these rows
if "počet" in penalty_rows.columns:
    penalty_rows.rename(columns={"počet": "částka"}, inplace=True)

# Separate the remaining rows
remaining_rows = df[df["typ dat"] != "Uložené pokuty v Kč"].copy()

# Ensure 'částka' column is added to remaining rows with NaN values using .loc
remaining_rows.loc[:, "částka"] = pd.NA

# Ensure the 'počet' column is in the penalty_rows DataFrame
if "počet" not in penalty_rows.columns:
    penalty_rows.loc[:, "počet"] = pd.NA

# Reorder columns for both DataFrames to match the new structure
remaining_rows = remaining_rows[
    ["období", "obvod", "typ dat", "kategorie", "přestupek", "počet", "částka"]
]
penalty_rows = penalty_rows[
    ["období", "obvod", "typ dat", "kategorie", "přestupek", "počet", "částka"]
]

# Merge the dataframes back together
df_final = pd.concat([remaining_rows, penalty_rows], ignore_index=True)

# Remove leading and trailing whitespaces from all the string columns
df_final = df_final.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Remove rows which contain 'celkem' in any of the columns, case insensitive
df_final = df_final[
    ~df_final.apply(lambda x: x.str.contains("celkem", case=False, na=False)).any(
        axis=1
    )
]

# Fix a typo in the typ dat column - zjitěných -> zjištěných
df_final["typ dat"] = df_final["typ dat"].str.replace("zjitěných", "zjištěných")

# Convert the 'období' column to datetime. It's in the format 'MMYYYY'
období = df_final["období"].astype(str)
df_final["období"] = pd.to_datetime(období, format="%m%Y", errors="coerce")

# Remove "z toho: " from přestupek column
df_final["přestupek"] = df_final["přestupek"].str.replace("z toho: ", "")

# Remove spaces from the 'počet' and 'částka' columns and convert them to numeric
df_final["počet"] = pd.to_numeric(
    df_final["počet"].str.replace(" ", ""), errors="coerce"
)
df_final["částka"] = pd.to_numeric(
    df_final["částka"].str.replace(" ", ""), errors="coerce"
)

# Convert 'počet' and 'částka' columns to integers (nullable integers - so that we can have blank values in the CSV file and no decimal points)
df_final["počet"] = df_final["počet"].astype("Int64")
df_final["částka"] = df_final["částka"].astype("Int64")

# Save the DataFrame to a CSV file
csv_file_path = "data/output/MP_Praha_2024.csv"

# Make directory if it doesn't exist
os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

df_final.to_csv(csv_file_path, index=False)

print(f"Data successfully converted and saved to {csv_file_path}")

# try to replace the last line in README.md with the current date
try:
    with open("README.md", "r") as f:
        lines = f.readlines()
        if lines[-1].startswith("Poslední aktualizace:"):
            lines[-1] = (
                f"Poslední aktualizace: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n"
            )
        else:
            lines.append(
                f"Poslední aktualizace: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n"
            )

    with open("README.md", "w") as f:
        f.writelines(lines)
except Exception as e:
    print(f"Failed to update the last line in README.md: {e}")
