import pandas as pd


def calculate_average_temperature(df_countries_cities_weather: pd.DataFrame, dates: pd.Series) -> pd.DataFrame:
    avg_temp_per_day_global = pd.DataFrame(index=['date'], columns=['avg_temp_c'])
    for date in dates:
        avg_temp_per_day_global.loc[date] = \
            df_countries_cities_weather[df_countries_cities_weather['date'] == str(date)]['avg_temp_c'].mean()

    return avg_temp_per_day_global


def aggregate_average_temperature_on_continent_scale(df_countries_cities_weather: pd.DataFrame, dates: pd.Series,
                                                     continent: str) -> pd.DataFrame:
    df_countries_cities_weather_in_continent = df_countries_cities_weather[
        df_countries_cities_weather['continent'] == continent]

    return calculate_average_temperature(df_countries_cities_weather_in_continent, dates)


def aggregate_average_precipitation(df_countries_cities_weather: pd.DataFrame,
                                    dates: pd.Series) -> pd.DataFrame:
    avg_precipitation_per_day = pd.DataFrame(index=['date'], columns=['avg_precipitation_mm'])
    for date in dates:
        avg_precipitation_per_day.loc[date] = \
            df_countries_cities_weather[df_countries_cities_weather['date'] == str(date)]['precipitation_mm'].mean()

    return avg_precipitation_per_day


def aggregate_average_precipitation_on_continent_scale(df_countries_cities_weather: pd.DataFrame, dates: pd.Series,
                                                       continent: str) -> pd.DataFrame:
    df_countries_cities_weather_in_contintent = df_countries_cities_weather[
        df_countries_cities_weather['continent'] == continent]

    return aggregate_average_precipitation(df_countries_cities_weather_in_contintent, dates)
