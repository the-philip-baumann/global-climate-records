import pandas as pd


def calculate_temperature_for_country(df_countries_cities_weather: pd.DataFrame, country: str):
    df_countries_cities_weather_for_country = df_countries_cities_weather[
        df_countries_cities_weather['country'] == country][['date', 'avg_temp_c', 'min_temp_c', 'max_temp_c']]

    return df_countries_cities_weather_for_country.melt(id_vars='date', var_name='Category', value_name='Temperatures')


def calculate_precipitation_mm_for_country(df_countries_cities_weather: pd.DataFrame, country: str) -> pd.DataFrame:
    df_precipitation_for_country = \
        df_countries_cities_weather[df_countries_cities_weather['country'] == country][['date', 'precipitation_mm']]

    return df_precipitation_for_country
