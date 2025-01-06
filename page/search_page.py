from typing import Tuple
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots

countries_continent = pd.DataFrame()


def search_page():
    global countries_continent

    df_global_map = gpd.read_file("./data/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp")
    df_countries_avg_temperatures = pd.read_csv('./data/countries_avg_temperatures.csv')
    df_countries = pd.read_csv('./data/countries_extended.csv')

    df_global_map_with_temperatures = pd.merge(df_global_map, df_countries_avg_temperatures, on='NAME', how='left')

    df_countries = df_countries[df_countries_avg_temperatures['avg_temp_c'].notna()][['country', 'continent', 'NAME']]

    df_continents = pd.DataFrame(df_countries['continent'].dropna().unique(), columns=['continent'])
    continents = df_continents['continent']
    continents.loc[len(continents)] = "All"

    if 'selection_box_continent' not in st.session_state:
        st.session_state.selection_box_continent = "All"

    if 'selection_box_country' not in st.session_state:
        st.session_state.selection_box_country = df_countries.iloc[0]['country']

    container = st.container()

    countries_continent = df_countries[['country', 'continent']]

    continent, country = container.columns(2)
    continent.selectbox(
        'Continent:',
        continents,
        key='selection_box_continent',
        on_change=on_change_continent()
    )

    country.selectbox(
        'Country:',
        countries_continent['country'],
        key='selection_box_country',
    )

    selected_country = df_countries[df_countries['country'] == st.session_state.selection_box_country]['NAME'].values[0]
    min_temperature = df_global_map_with_temperatures['avg_temp_c'].min()
    max_temperature = df_global_map_with_temperatures['avg_temp_c'].max()

    country_fig, country_avg_temperature = create_country_map_plot(df_global_map_with_temperatures,
                                                                   (selected_country, min_temperature, max_temperature))

    st.title(f'{selected_country} - ({country_avg_temperature} °C)')

    st.pyplot(country_fig, use_container_width=True)

    detail_graphs(df_countries)


def on_change_continent() -> None:
    global countries_continent
    current_value = st.session_state['selection_box_continent']
    if not current_value == "All":
        countries_continent = countries_continent[countries_continent['continent'] == current_value]


def create_country_map_plot(df_global_map_with_temperatures: pd.DataFrame, selected_country: Tuple[str, float, float]):
    crossing_countries = ['New Zealand', 'Fiji', 'Russia', 'Kiribati']
    country, min_temp, max_temp = selected_country
    cmap = create_cmap()

    selected_county_map = df_global_map_with_temperatures[df_global_map_with_temperatures['NAME'] == country]
    if st.session_state.selection_box_country in crossing_countries:
        sub_fig, sub_ax = plt.subplots(figsize=(20, 5))
    else:
        sub_fig, sub_ax = plt.subplots(figsize=(70, 3))
    selected_county_map.boundary.plot(ax=sub_ax, linewidth=0.1, color='black')
    selected_county_map.plot(column='avg_temp_c', legend=True, ax=sub_ax, cmap=cmap, vmin=min_temp,
                             vmax=max_temp, legend_kwds={'label': 'Temperature [°C]'},
                             missing_kwds={'color': 'grey'})
    sub_ax.axis('off')
    return sub_fig, selected_county_map['avg_temp_c'].values[0]


def create_cmap():
    colors = ['#A3DFFB', '#FFFFFF', '#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
    return mcolors.LinearSegmentedColormap.from_list('heatmap', colors)


def detail_graphs(df_countries: pd.DataFrame):
    subplots = make_subplots(rows=1, cols=2, shared_xaxes=True, subplot_titles=['Average Temperature', 'Average Precipitation'])

    box_country = df_countries[df_countries['country'] == st.session_state["selection_box_country"]][['NAME', 'continent']]
    df_detail_temperatures_full = pd.read_csv(f'./data/country_detail/{box_country.values[0][0]}.csv')
    df_detail_temperatures = df_detail_temperatures_full[['date', 'avg_temp_c', 'min_temp_c', 'max_temp_c']]
    df_detail_temperatures = df_detail_temperatures.melt(id_vars=['date'], var_name='category', value_name='value')

    detail_temperatures_line_chart = px.line(
        df_detail_temperatures,
        x='date',
        y='value',
        color='category',
        title='Temperatures',
    )

    average_temperature_of_continent = px.line(
        df_detail_temperatures_full[['date', 'avg_temp_c_continent']],
        x='date',
        y='avg_temp_c_continent',
    )
    average_temperature_of_continent.update_traces(fill='tozeroy', fillcolor='rgba(0, 0, 0, 0.15)')

    df_detail_precipitation = df_detail_temperatures_full[['date', 'precipitation_mm']]
    detail_precipitation_line_chart = px.line(
        df_detail_precipitation,
        x='date',
        y='precipitation_mm',
        title='Precipitation in mm',
    )
    detail_precipitation_line_chart.update_layout(showlegend=True)
    average_precipitation_of_continent = px.line(
        df_detail_temperatures_full[['date', 'precipitation_mm_continent']],
        x='date',
        y='precipitation_mm_continent',
    )
    average_precipitation_of_continent.update_traces(fill='tozeroy', fillcolor='rgba(0, 0, 139, 0.15)')

    for trace in detail_temperatures_line_chart.data:
        subplots.add_trace(trace, row=1, col=1)

    for trace in average_temperature_of_continent.data:
        subplots.add_trace(trace, row=1, col=1)

    for trace in detail_precipitation_line_chart.data:
        subplots.add_trace(trace, row=1, col=2)

    for trace in average_precipitation_of_continent.data:
        subplots.add_trace(trace, row=1, col=2)

    subplots.update_xaxes(
        range=['2022-01-01', '2022-12-31'],
        row=1,
        col=1,
        title_text="Time"
    )
    subplots.update_yaxes(row=1, col=1, title_text="Temperature [°C]")

    subplots.update_xaxes(
        range=['2022-01-01', '2022-12-31'],
        row=1,
        col=2,
        title_text="Time"
    )
    subplots.update_yaxes(row=1, col=2, title_text="Precipitation [mm]")

    subplots.data[0].name = 'Average Temperature'
    subplots.data[1].name = 'Minimum Temperature'
    subplots.data[2].name = 'Maximum Temperature'
    subplots.data[3].name = f'Average Temperature in {box_country.values[0][1]}'
    subplots.data[4].name = 'Precipitation'
    subplots.data[5].name = f'Average Precipitation in {box_country.values[0][1]}'

    subplots.data[0].line.color = "#808080"
    subplots.data[2].line.color = "#FF0000"
    subplots.data[3].line.color = "rgba(0, 0, 0, 0.2)"
    subplots.data[5].line.color = "rgba(0, 0, 139, 0.2)"

    subplots.update_traces(showlegend=True)

    st.plotly_chart(subplots)
