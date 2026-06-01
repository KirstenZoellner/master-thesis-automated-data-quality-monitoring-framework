import pandas as pd

df = pd.read_parquet("data/daily_weather_clean.parquet").copy()

# Fehler 1: 31 NULL-Werte in city_name
idx = df.sample(n=31, random_state=101).index
df.loc[idx, "city_name"] = None

# Fehler 2: 504 Duplikate über station_id + date
duplicates = df.sample(n=504, random_state=102)
df_technical = pd.concat([df, duplicates], ignore_index=True)

df_technical.to_parquet("data/daily_weather_technical.parquet", index=False)

print("Technical Data erstellt")
print("Zeilen:", len(df_technical))