SELECT
    station_id,
    city_name,
    date,
    season,

    avg_temp_c,
    min_temp_c,
    max_temp_c,

    precipitation_mm,
    snow_depth_mm,

    avg_wind_dir_deg,
    avg_wind_speed_kmh,

    peak_wind_gust_kmh,
    avg_sea_level_pres_hpa,

    sunshine_total_min

FROM `project-b27d4192-1221-4ffd-b03.weather_dq.{{ var('weather_table') }}`