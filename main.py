import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np


from data_preprocessing import preprocess
from climate_averages import aggregate_average_temperature, \
    aggregate_average_precipitation, aggregate_average_temperature_on_continent_scale, \
    aggregate_average_precipitation_on_continent_scale
from climate_extremes import calculate_warmest_countries, calculate_coldest_countries
from climate_detail import calculate_precipitation_mm_for_country, calculate_temperature_for_country

# Streamlint Config
st.set_page_config(layout="wide")
if 'selection_box_continent' not in st.session_state:
    st.session_state.selection_box_continent = 'All'

if 'selection_box_country' not in st.session_state:
    st.session_state.selection_box_country = 'All'

df_weather = pd.read_parquet('./data/daily_weather.parquet')
df_weather = df_weather[
    ['station_id', 'city_name', 'date', 'season', 'avg_temp_c', 'min_temp_c', 'max_temp_c', 'precipitation_mm']]

df_countries = pd.read_csv('./data/countries_extended.csv')
df_countries = df_countries[['country', 'capital', 'continent', 'NAME']]

df_global_map = gpd.read_file("data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")

df_cities = pd.read_csv("./data/cities.csv")
df_cities = df_cities[['country', 'station_id']]

df_countries_cities_weather = preprocess(df_weather, df_countries, df_cities)
df_global_map_with_temperatures = pd.merge(df_global_map, df_countries_cities_weather, on='NAME', how='left')

dates = df_countries_cities_weather['date'].drop_duplicates().sort_values().dt.date
df_continents = df_countries['continent'].dropna().unique()

df_countries_selections = df_countries.copy()
countries = df_countries_selections['country'].dropna().unique()
countries = np.insert(countries, 0, 'All')

df_continents_selections = df_continents.copy()
continents = np.insert(df_continents_selections, 0, 'All')

st.write(f'Global Climat Records - ({st.session_state["selection_box_country"]})')

container = st.container()



def on_change_continent() -> None:
    global countries
    current_value = st.session_state['selection_box_continent']
    if not current_value == 'All':
        countries = df_countries_selections[df_countries_selections['continent'] == current_value][
            'country'].dropna().unique()

# Filter Form
continent, country = container.columns(2)
continent.selectbox(
    'Continent:',
    continents,
    key='selection_box_continent',
    on_change=on_change_continent()
)
country.selectbox(
    'Country:',
    countries,
    key='selection_box_country',
)

st.write('**Average Temperature Classification**')

min_temperature = df_global_map_with_temperatures['avg_temp_c'].min()
max_temperature = df_global_map_with_temperatures['avg_temp_c'].max()

if st.session_state.selection_box_country == 'All':
    fig, ax = plt.subplots(figsize=(40, 10))
    df_global_map_with_temperatures.plot(column='avg_temp_c', ax=ax, legend=True, cmap='YlOrRd', vmin=min_temperature, vmax=max_temperature, legend_kwds={'label': 'Average Temperature'}, missing_kwds={'color': 'grey'})
    df_global_map_with_temperatures.boundary.plot(ax=ax, linewidth=0.1, color='black')
    ax.axis('off')
    st.pyplot(fig)
else:
    country = df_countries[df_countries['country'] == st.session_state.selection_box_country]
    selected_county_map = df_global_map_with_temperatures[df_global_map_with_temperatures['NAME'] == country['NAME'].values[0]]
    sub_fig, sub_ax = plt.subplots(figsize=(20, 20))
    selected_county_map.boundary.plot(ax=sub_ax, linewidth=0.1, color='black')
    selected_county_map.plot(column='avg_temp_c', legend=True, ax=sub_ax, cmap='YlOrRd', vmin=min_temperature, vmax=max_temperature, legend_kwds={'label': 'Average Temperature'}, missing_kwds={'color': 'grey'})
    sub_ax.axis('off')
    st.pyplot(sub_fig, use_container_width=True)


col_left, col_right = st.columns(2)

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

df_detail_temperatures = calculate_temperature_for_country(df_countries_cities_weather, st.session_state['selection_box_country'])
detail_temperatures_line_chart = px.line(
    df_detail_temperatures,
    x='date',
    y='Temperatures',
    color='Category',
    title='Temperatures',
)

df_detail_precipitation = calculate_precipitation_mm_for_country(df_countries_cities_weather, st.session_state['selection_box_country'])
detail_precipitation_line_chart = px.line(
    df_detail_precipitation,
    x='date',
    y='precipitation_mm',
    title='Precipitation in mm',
)

if st.session_state.selection_box_country == 'All':
    col_left.plotly_chart(average_precipitation_line_chart)
    col_left.plotly_chart(top_ten_warmest_countries_line_chart)

    col_right.plotly_chart(average_temp_line_chart)
    col_right.plotly_chart(top_ten_coldest_countries_line_chart)
else:
    col_left.plotly_chart(detail_temperatures_line_chart)
    col_right.plotly_chart(detail_precipitation_line_chart)
