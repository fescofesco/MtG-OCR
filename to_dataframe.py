import pandas as pd

data = [
    [
        "\"Festerleech\"",
        1,
        "\"Creature - Zombie Leech\"",
        "B",
        "\"mkm\"",
        "\"85\"",
        "uncommon",
        "b",
        "Owned",
        "",
        "",
        "",
        "\"\"",
        "\"\"",
        121648
    ],
    [
      "\"Urborg Scavengers\"",
      3,
      "\"Creature - Spirit\"",
      "B",
      "\"mat\"",
      "\"15\"",
      "rare",
      "b",
      "Owned",
      "Foil",
      "",
      "",
      "\"\"",
      "\"\"",
      109152
    ]

]

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Define column names
column_names = ["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"]

# Label the DataFrame columns
df.columns = column_names

print(df)
