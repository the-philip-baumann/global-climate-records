import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from data_preprocessing import preprocess
from climate_averages import aggregate_average_temperature, \
    aggregate_average_precipitation, aggregate_average_temperature_on_continent_scale, \
    aggregate_average_precipitation_on_continent_scale
from climate_extremes import calculate_warmest_countries, calculate_coldest_countries

# Streamlint Config
st.set_page_config(layout="wide")

df_weather = pd.read_parquet('./data/daily_weather.parquet')
df_weather = df_weather[
    ['station_id', 'city_name', 'date', 'season', 'avg_temp_c', 'min_temp_c', 'max_temp_c', 'precipitation_mm']]

df_countries = pd.read_csv('./data/countries.csv')
df_countries = df_countries[['country', 'capital', 'continent']]

df_cities = pd.read_csv("./data/cities.csv")
df_cities = df_cities[['country', 'station_id']]

df_countries_cities_weather = preprocess(df_weather, df_countries, df_cities)

dates = df_countries_cities_weather['date'].drop_duplicates().sort_values().dt.date
df_continents = df_countries['continent'].dropna().unique()

df_countries_selections = df_countries.copy()
countries = df_countries_selections['country'].dropna().unique()
countries = np.insert(countries, 0, 'All')

df_continents_selections = df_continents.copy()
continents = np.insert(df_continents_selections, 0, 'All')

st.write('Global Climat Records')

container = st.container()

col_left, col_right = st.columns(2)


def on_change_continent() -> None:
    selected = st.session_state['selection_box_continent']
    st.write(f'This is a test: {selected}')
    # print(selected)


# Filter Form
with container.form(key='filter_form'):

    st.write("Country Filter")
    continent, country = st.columns(2)
    continent.selectbox(
        'Continent:',
        continents,
        key='selection_box_continent',
        on_change=on_change_continent()
    )
    country.selectbox(
        'Country:',
        countries
    )

    st.form_submit_button("Search")

# Average Temperature
df_aggregated_average_temp = aggregate_average_temperature(df_countries_cities_weather, dates)
for continent in df_continents:
    df_aggregated_average_temp[continent] = aggregate_average_temperature_on_continent_scale(
        df_countries_cities_weather, dates, continent)

average_temp_line_chart = px.line(
    df_aggregated_average_temp,
    title='Average Temperature',
)

# Average Precipitation
df_aggreated_precipitation = aggregate_average_precipitation(df_countries_cities_weather, dates)
for continent in df_continents:
    df_aggreated_precipitation[continent] = aggregate_average_precipitation_on_continent_scale(
        df_countries_cities_weather, dates, continent)

average_precipitation_line_chart = px.line(
    df_aggreated_precipitation,
    title='Average Precipitation',
)

# Top ten warmest countries
df_top_ten_warmest_countries = calculate_warmest_countries(df_countries_cities_weather, dates)
top_ten_warmest_countries_line_chart = px.line(
    df_top_ten_warmest_countries,
    x='date',
    y='max_temp_c',
    color='country',
    title='Top 10 Warmest Countries',
)

# Top ten coldest countries
df_top_ten_coldest_countries = calculate_coldest_countries(df_countries_cities_weather, dates)
top_ten_coldest_countries_line_chart = px.line(
    df_top_ten_coldest_countries,
    x='date',
    y='min_temp_c',
    color='country',
    title='Top 10 Coldest Countries',
)

col_left.plotly_chart(average_precipitation_line_chart)
col_left.plotly_chart(top_ten_warmest_countries_line_chart)

col_right.plotly_chart(average_temp_line_chart)
col_right.plotly_chart(top_ten_coldest_countries_line_chart)
