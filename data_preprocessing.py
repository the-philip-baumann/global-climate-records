import pandas as pd
import datetime as dt


def preprocess(df_weather: pd.DataFrame, df_countries: pd.DataFrame, df_cities: pd.DataFrame) -> pd.DataFrame:
    df_weather_cleaned = df_weather.dropna(subset=['avg_temp_c'])
    df_weather_cleaned.loc[:, 'date'] = pd.to_datetime(df_weather_cleaned['date']).dt.date
    df_weather_cleaned = df_weather_cleaned[df_weather_cleaned['date'] >= pd.to_datetime(dt.date(2020, 1, 1))]

    df_cities_country = pd.merge(df_countries, df_cities, on='country')
    df_cities_country = df_cities_country.drop_duplicates(subset=['capital'])

    return pd.merge(df_cities_country, df_weather_cleaned, on='station_id', how='inner')
