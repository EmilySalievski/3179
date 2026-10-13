from pathlib import Path
import pandas as pd

# Find the OpenPowerlifting CSV in the same folder as this script.
HERE = Path(__file__).parent
files = sorted(HERE.glob("openpowerlifting-*.csv"))

if not files:
    raise FileNotFoundError(
        "No openpowerlifting-*.csv file found in this folder."
    )

csv_path = files[-1]
output_path = HERE / "top5_australian_meets_2025.csv"

print(f"Reading {csv_path.name}...")

# Load only the columns needed for this task.
df = pd.read_csv(
    csv_path,
    usecols=[
        "Name",
        "Date",
        "MeetCountry",
        "MeetState",
        "MeetTown",
        "MeetName",
        "Federation",
    ],
    low_memory=False,
)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Filter to Australian competitions held in 2025.
meets = df[
    df["MeetCountry"]
    .astype("string")
    .str.strip()
    .str.casefold()
    .eq("australia")
    & (df["Date"].dt.year == 2026)
    & df["MeetName"].notna()
].copy()

if meets.empty:
    print("No Australian meets from 2025 found.")
    print("Available MeetCountry values:")
    print(df["MeetCountry"].value_counts(dropna=False).head(20))
    raise SystemExit

# Count unique lifters in each competition.
group_columns = [
    "Date",
    "MeetName",
    "Federation",
    "MeetCountry",
    "MeetState",
    "MeetTown",
]

top10 = (
    meets.groupby(group_columns, dropna=False)
    .agg(participants=("Name", "nunique"))
    .reset_index()
    .sort_values("participants", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

top10.insert(0, "Rank", range(1, len(top10) + 1))
top10["Date"] = top10["Date"].dt.strftime("%Y-%m-%d")

# Print the results.
columns = [
    "Rank",
    "Date",
    "MeetName",
    "Federation",
    "MeetTown",
    "MeetState",
    "participants",
]

print("\nTop 5 Australian powerlifting competitions in 2025:\n")
print(top10[columns].to_string(index=False))

# Save the results to a CSV for later use.
top10.to_csv(output_path, index=False)
print(f"\nResults saved to: {output_path}")