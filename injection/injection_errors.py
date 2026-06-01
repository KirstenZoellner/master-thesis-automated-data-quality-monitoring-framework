import pandas as pd

# Wetterdaten laden
df = pd.read_parquet("data/daily_weather_sample.parquet")

# Fehler 1: NULL-Werte
idx = df.sample(frac=0.05, random_state=42).index
df.loc[idx, "avg_temp_c"] = None

# Fehler 2: unplausible Temperaturwerte
idx = df.sample(frac=0.01, random_state=43).index
df.loc[idx, "max_temp_c"] = -999

# Fehler 3: Duplikate
duplicates = df.sample(n=500, random_state=44)
df_faulty = pd.concat([df, duplicates], ignore_index=True)

# Fehler 4: veraltete Daten / Timeliness
# simuliert: aktuellster Messwert liegt mindestens 3 Tage zurück
df_faulty["date"] = pd.to_datetime(df_faulty["date"]) - pd.Timedelta(days=3)

# Fehler 5: logischer Widerspruch min_temp_c > max_temp_c
idx = df_faulty.sample(n=200, random_state=45).index
df_faulty.loc[idx, "min_temp_c"] = 25
df_faulty.loc[idx, "max_temp_c"] = 12

# Speichern
df_faulty.to_parquet("data/daily_weather_faulty.parquet", index=False)

print("daily_weather_faulty.parquet erstellt")


# Fehler 6: Formatabweichung in cities.csv
# Ziel: ungültige ISO-Ländercodes erzeugen

import pandas as pd

cities = pd.read_csv("data/cities.csv")

# 25 falsche 3-stellige Codes
idx = cities.sample(n=25, random_state=46).index
cities.loc[idx, "country_code"] = "GER"

# weitere 25 mit Regionalcode
remaining = cities.drop(idx)

idx2 = remaining.sample(n=25, random_state=47).index
cities.loc[idx2, "country_code"] = "DE-NW"

# Speichern
cities.to_csv(
    "data/cities_faulty.csv",
    index=False
)

print("cities_faulty.csv erstellt")