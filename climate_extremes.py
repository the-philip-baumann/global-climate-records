import pandas as pd

# TODO: Calculations are wrong

def calculate_warmest_countries(df_countries_cities_weather: pd.DataFrame, dates: pd.Series) -> pd.DataFrame:
    scores = {}
    df_countries_cities_weather['max_temp_c'] = df_countries_cities_weather['max_temp_c'].fillna(df_countries_cities_weather['avg_temp_c'])

    for date in dates:
        df_country_max_temp_c = df_countries_cities_weather[df_countries_cities_weather['date'] == str(date)][
            ['country', 'max_temp_c']]
        df_country_max_temp_c.nlargest(10, 'max_temp_c')
        for record in df_country_max_temp_c.nlargest(10, 'max_temp_c').itertuples(index=True):
            scores[record.country] = scores.get(record.country, 0.0) + record.max_temp_c

    df_scores = pd.DataFrame.from_dict(scores, orient='index', columns=['score']).reset_index()
    df_scores = df_scores.rename(columns={'index': 'country'})
    df_scores_top_ten = df_scores.nlargest(10, 'score')

    result = pd.DataFrame(index=['date'], columns=df_countries_cities_weather.columns)
    df_reduced_countries_weather = df_countries_cities_weather[
        df_countries_cities_weather['country'].isin(df_scores_top_ten['country'])]

    for date in dates:
        df_countries_cities_weather_date = df_reduced_countries_weather[
            (df_countries_cities_weather['date'] == str(date))]
        result = pd.concat([result, df_countries_cities_weather_date], ignore_index=True)

    return result


def calculate_coldest_countries(df_countries_cities_weather: pd.DataFrame, dates: pd.Series) -> pd.DataFrame:
    scores = {}
    df_countries_cities_weather['min_temp_c'] = df_countries_cities_weather['min_temp_c'].fillna(df_countries_cities_weather['avg_temp_c'])

    for date in dates:
        df_country_max_temp_c = df_countries_cities_weather[df_countries_cities_weather['date'] == str(date)][
            ['country', 'min_temp_c']]
        df_country_max_temp_c.nsmallest(10, 'min_temp_c')
        for record in df_country_max_temp_c.nsmallest(10, 'min_temp_c').itertuples(index=True):
            scores[record.country] = scores.get(record.country, 0.0) + record.min_temp_c

    df_scores = pd.DataFrame.from_dict(scores, orient='index', columns=['score']).reset_index()
    df_scores = df_scores.rename(columns={'index': 'country'})
    df_scores_top_ten = df_scores.nsmallest(10, 'score')

    result = pd.DataFrame(index=['date'], columns=df_countries_cities_weather.columns)
    df_reduced_countries_weather = df_countries_cities_weather[
        df_countries_cities_weather['country'].isin(df_scores_top_ten['country'])]

    for date in dates:
        df_countries_cities_weather_date = df_reduced_countries_weather[
            (df_countries_cities_weather['date'] == str(date))]
        result = pd.concat([result, df_countries_cities_weather_date], ignore_index=True)

    return result
