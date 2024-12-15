import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
from io import BytesIO

# Streamlint Config
st.set_page_config(layout="wide")

if 'selection_box_continent' not in st.session_state:
    st.session_state.selection_box_continent = 'All'

if 'selection_box_country' not in st.session_state:
    st.session_state.selection_box_country = 'All'

df_weather = pd.read_parquet('./data/weather_compressed.parquet')
df_weather = df_weather[['country', 'date', 'avg_temp_c', 'min_temp_c', 'max_temp_c', 'precipitation_mm']]

df_countries = pd.read_csv('./data/countries_extended.csv')
df_countries = df_countries[['country', 'capital', 'continent', 'NAME']]

df_global_map = gpd.read_file("data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")

df_cities = pd.read_csv("data/cities.csv")
df_cities = df_cities[['country', 'station_id']]

df_countries_avg_temperature = pd.read_csv('./data/countries_avg_temperatures.csv')
df_global_map_with_temperatures = pd.merge(df_global_map, df_countries_avg_temperature, on='NAME', how='left')

df_continents = df_countries['continent'].dropna().unique()
df_continents_selections = df_continents.copy()
continents = np.insert(df_continents_selections, 0, 'All')

def create_cmap():
    colors = ['#FFFFFF', '#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
    return mcolors.LinearSegmentedColormap.from_list('heatmap', colors)

st.title(f'Global Climat Records 01.1960-09.2023 - ({st.session_state["selection_box_country"]})')

container = st.container()

st.write('**Average Temperature Classification**')

min_temperature = df_global_map_with_temperatures['avg_temp_c'].min()
max_temperature = df_global_map_with_temperatures['avg_temp_c'].max()

if st.session_state.selection_box_country == 'All':
    fig, ax = plt.subplots(figsize=(40, 10))
    df_global_map_with_temperatures.plot(column='avg_temp_c', ax=ax, legend=True, cmap=create_cmap(), vmin=min_temperature, vmax=max_temperature, legend_kwds={'label': 'Temperature in Celsius'}, missing_kwds={'color': 'grey'})
    df_global_map_with_temperatures.boundary.plot(ax=ax, linewidth=0.1, color='black')
    ax.axis('off')
    no_data_patch = mpatches.Patch(color='grey', label='No Data')
    plt.legend(handles=[no_data_patch], loc='lower right')
    st.pyplot(fig)
else:
    crossing_countries = ['New Zealand', 'Fiji', 'Russia', 'Kiribati']
    country = df_countries[df_countries['country'] == st.session_state.selection_box_country]
    selected_county_map = df_global_map_with_temperatures[df_global_map_with_temperatures['NAME'] == country['NAME'].values[0]]
    if st.session_state.selection_box_country in crossing_countries:
        sub_fig, sub_ax = plt.subplots(figsize=(20, 5))
    else:
        sub_fig, sub_ax = plt.subplots(figsize=(70, 3))

    selected_county_map.boundary.plot(ax=sub_ax, linewidth=0.1, color='black')
    selected_county_map.plot(column='avg_temp_c', legend=True, ax=sub_ax, cmap=create_cmap(), vmin=min_temperature, vmax=max_temperature, legend_kwds={'label': 'Temperature in Celsius'}, missing_kwds={'color': 'grey'})
    sub_ax.axis('off')
    st.pyplot(sub_fig, use_container_width=True)

col_left, col_right = st.columns(2)

# Filter Form
countries = df_countries[['country', 'continent']]
df_all = pd.DataFrame([['All', '']], columns=countries.columns)
countries = pd.concat([df_all, countries])

def on_change_continent() -> None:
    global countries
    current_value = st.session_state['selection_box_continent']
    if not current_value == 'All':
        countries = countries[countries['continent'] == current_value]


continent, country = container.columns(2)
continent.selectbox(
    'Continent:',
    continents,
    key='selection_box_continent',
    on_change=on_change_continent()
)

country.selectbox(
    'Country:',
    countries['country'],
    key='selection_box_country',
)

continent_colors = {
    "Africa": 'rgb(255, 140, 0)',
    "Asia": 'rgb(255, 0, 0)',
    "Europe": 'rgb(0, 128, 128)',
    "North America": 'rgb(0, 255, 0)',
    "South America": 'rgb(255, 255, 0)',
    "Oceania": 'rgb(139, 69, 19)',
    "open ocean": 'rgb(0, 0, 255)'
}


# Average Temperature
df_aggregated_average_temp = pd.read_csv('./data/country_overall/average_temp_per_day_global.csv')
average_temp_line_chart = px.line(
    df_aggregated_average_temp,
    x='date',
    y='avg_temp_c',
    color='continent',
    title='Average Temperature',
    color_discrete_map=continent_colors
)
average_temp_line_chart.update_layout(
    xaxis_title='Year',  # Rename x-axis
    yaxis_title='Temperature in Celsius'   # Rename y-axis
)

# Average Precipitation
df_aggregated_average_precipitation = pd.read_csv('./data/country_overall/average_precipitation_per_day_global.csv')
average_precipitation_line_chart = px.line(
    df_aggregated_average_precipitation,
    x='date',
    y='precipitation_mm',
    color='continent',
    title='Average Precipitation',
    color_discrete_map=continent_colors
)
average_precipitation_line_chart.update_layout(
    xaxis_title='Year',  # Rename x-axis
    yaxis_title='Precipitation in millimeters'   # Rename y-axis
)

colors_hot = [
    'rgb(139, 0, 0)',
    'rgb(255, 0, 0)',
    'rgb(255, 69, 0)',
    'rgb(255, 140, 0)',
    'rgb(255, 204, 0)'
]
# Top ten warmest countries
df_top_ten_warmest_countries = pd.read_csv('./data/country_overall/top_5_warmest_countries.csv')
top_ten_warmest_countries_line_chart = px.line(
    df_top_ten_warmest_countries,
    x='date',
    y='max_temp_c',
    color='country',
    title='Top 5 Warmest Countries',
    color_discrete_sequence=colors_hot
)
top_ten_warmest_countries_line_chart.update_layout(
    xaxis_title='Year',  # Rename x-axis
    yaxis_title='Temperature in Celsius'   # Rename y-axis
)


# Top ten coldest countries
cold_colors = [
    'rgb(173, 216, 230)',
    'rgb(0, 191, 255)',
    'rgb(135, 206, 235)',
    'rgb(70, 130, 180)',
    'rgb(0, 0, 139)',
]
df_top_ten_coldest_countries = pd.read_csv('./data/country_overall/top_5_coldest_countries.csv')
top_ten_coldest_countries_line_chart = px.line(
    df_top_ten_coldest_countries,
    x='date',
    y='min_temp_c',
    color='country',
    title='Top 5 Coldest Countries',
    color_discrete_sequence=cold_colors,
)
top_ten_coldest_countries_line_chart.update_layout(
    xaxis_title='Year',  # Rename x-axis
    yaxis_title='Temperature in Celsius'   # Rename y-axis
)

if st.session_state.selection_box_country == 'All':
    col_left.plotly_chart(average_temp_line_chart)
    col_left.plotly_chart(top_ten_warmest_countries_line_chart)

    col_right.plotly_chart(average_precipitation_line_chart)
    col_right.plotly_chart(top_ten_coldest_countries_line_chart)
else:
    #Todo clarify if "NAME" or "country" should be used
    box_country = df_countries[df_countries['country'] == st.session_state["selection_box_country"]]['NAME']
    df_detail_temperatures_full = pd.read_csv(f'./data/country_detail/{box_country.values[0]}.csv')
    df_detail_temperatures = df_detail_temperatures_full[['date', 'avg_temp_c', 'min_temp_c', 'max_temp_c']]
    df_detail_temperatures = df_detail_temperatures.melt(id_vars=['date'], var_name='category', value_name='value')
    detail_temperatures_line_chart = px.line(
        df_detail_temperatures,
        x='date',
        y='value',
        color='category',
        title='Temperatures',
    )
    col_left.plotly_chart(detail_temperatures_line_chart)

    df_detail_precipitation = df_detail_temperatures_full[['date', 'precipitation_mm']]
    detail_precipitation_line_chart = px.line(
        df_detail_precipitation,
        x='date',
        y='precipitation_mm',
        title='Precipitation in mm',
        color_discrete_sequence=cold_colors
    )
    col_right.plotly_chart(detail_precipitation_line_chart)
