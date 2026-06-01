import pandas as pd

weather = pd.read_parquet("data/daily_weather_sample.parquet")
cities = pd.read_csv("data/cities.csv")

weather_clean = weather.copy()

weather_clean = weather_clean.dropna(
    subset=["station_id", "city_name", "date"]
)
weather_clean = weather_clean.drop_duplicates(subset=["station_id", "date"])

weather_clean = weather_clean[
    (weather_clean["avg_temp_c"] >= -90) &
    (weather_clean["avg_temp_c"] <= 60)
]

weather_clean = weather_clean[
    weather_clean["max_temp_c"] >= weather_clean["min_temp_c"]
]

cities_clean = cities.copy()
cities_clean = cities_clean[
    cities_clean["iso2"].str.match(r"^[A-Z]{2}$", na=False)
]

weather_clean.to_parquet("data/daily_weather_clean.parquet", index=False)
cities_clean.to_csv("data/cities_clean.csv", index=False)

print("Clean Sample erstellt")
print("Weather:", len(weather_clean))
print("Cities:", len(cities_clean))