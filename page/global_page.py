import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots


def global_page():
    # Streamlit layout
    st.title(f'Global Climate Records 2022')

    global_temperature_map = global_choropleth_map()

    subplots_top_row = make_subplots(rows=1, cols=2, shared_xaxes=True,
                                     subplot_titles=['Average Temperature', 'Average Precipitation'])

    average_temp = average_temperature()
    for trace in average_temp.data:
        subplots_top_row.add_trace(trace, row=1, col=1)

    average_precip = average_precipitation()
    for trace in average_precip.data:
        subplots_top_row.add_trace(trace, row=1, col=2)

    subplots_top_row.update_xaxes(
        range=['2022-01-01', '2022-12-31'],
        row=1,
        col=1,
        title_text="Time",
    )

    subplots_top_row.update_xaxes(
        range=['2022-01-01', '2022-12-31'],
        row=1,
        col=2,
        title_text="Time"
    )

    subplots_bottom_row = make_subplots(rows=1, cols=2, shared_xaxes=True,
                                        subplot_titles=['Warmest 5 Temperatures', 'Coldest 5 Temperatures'])

    warmest = warmest_countries()
    for trace in warmest.data:
        subplots_bottom_row.add_trace(trace, row=1, col=1)

    coldest = coldest_countries()
    for trace in coldest.data:
        subplots_bottom_row.add_trace(trace, row=1, col=2)

    subplots_top_row.update_yaxes(title_text="Temperature [°C]", row=1, col=1)
    subplots_top_row.update_yaxes(title_text="Precipitation [mm]", range=[0, 20], row=1, col=2)

    subplots_bottom_row.update_xaxes(
        range=['2022-01-01', '2022-12-31'],
        row=1,
        col=1,
        title_text="Time"
    )

    subplots_bottom_row.update_xaxes(
        range=['2022-01-01', '2022-12-31'],
        row=1,
        col=2,
        title_text="Time"
    )

    subplots_bottom_row.update_yaxes(title_text="Temperature [°C]")

    subplots_top_row.update_traces(row=1, col=1, showlegend=False)

    st.plotly_chart(global_temperature_map, use_container_width=True)
    st.plotly_chart(subplots_top_row)
    st.plotly_chart(subplots_bottom_row)

map_temperature_colors = [
    (0.00, '#A3DFFB'),
    (1 / 9, '#FFFFFF'),
    (2 / 9, '#FFEDA0'),
    (3 / 9, '#FED976'),
    (4 / 9, '#FEB24C'),
    (5 / 9, '#FD8D3C'),
    (6 / 9, '#FC4E2A'),
    (7 / 9, '#E31A1C'),
    (8 / 9, '#BD0026'),
    (9 / 9, '#800026')
]

continent_colors = {
    "Africa": '#e1bf92',
    "Asia": '#D32F2F',
    "Europe": '#4A90E2',
    "North America": '#70C1B3',
    "South America": '#FFD166',
    "Oceania": '#F08A5D',
    "all": '#341948'
}

start_day = pd.to_datetime('2022-01-01')
end_day = pd.to_datetime('2022-12-31')

x_range = st.session_state.get("x_range", [start_day, end_day])

def global_choropleth_map():
    # Data Preparation
    df_global_map = gpd.read_file("data/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp")
    df_countries_avg_temperatures = pd.read_csv('./data/countries_avg_temperatures.csv')
    df_global_map_with_temperatures = pd.merge(df_global_map, df_countries_avg_temperatures, on='NAME', how='left')

    # Define Global Map
    temperature_choropleth_map = px.choropleth(df_global_map_with_temperatures,
                                               geojson=df_global_map.geometry,
                                               locations=df_global_map.ISO_A3_EH,
                                               color='avg_temp_c',
                                               color_continuous_scale=map_temperature_colors,
                                               locationmode='ISO-3',
                                               hover_data={
                                                   'NAME': True,
                                                   'avg_temp_c': True,
                                               })

    # Chart labeling
    temperature_choropleth_map.update_layout(
        title='Average Temperature Classification',
        height=1000,
        coloraxis_colorbar=dict(
            title="Temperature [°C]",
            titleside="right",
            title_font=dict(size=20),
            tickfont=dict(size=20),
            thickness=50,
            ticklen=15
        )
    )

    # Handle countries with no data
    temperature_choropleth_map.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="#636363",
        resolution=50,
        showocean=True,
        oceancolor='#eeeeee'
    )


    temperature_choropleth_map.add_shape(
        type="rect",
        x0=0.99, y0=0.125,
        x1=1.01, y1=0.14,
        line=dict(color="#636363"),
        fillcolor="#636363",
    )

    temperature_choropleth_map.add_annotation(
        x=0.95,
        y=0.15,
        text="No Data:",
        showarrow=False,
        xanchor="center",
        yanchor="top",
        font=dict(size=18, color="black")
    )
    return temperature_choropleth_map


def average_temperature():
    # Average Temperature
    df_aggregated_average_temp = pd.read_csv('./data/country_overall/average_temp_per_day_global.csv')
    df_aggregated_average_temp = df_aggregated_average_temp[df_aggregated_average_temp != 'open ocean']
    average_temp_line_chart = px.line(
        df_aggregated_average_temp,
        x='date',
        y='avg_temp_c',
        color='continent',
        title='Average Temperature',
        color_discrete_map=continent_colors
    )

    return average_temp_line_chart


def average_precipitation():
    # Average Precipitation
    df_aggregated_average_precipitation = pd.read_csv('./data/country_overall/average_precipitation_per_day_global.csv')
    df_aggregated_average_precipitation = df_aggregated_average_precipitation[
        df_aggregated_average_precipitation != 'open ocean']
    average_precipitation_line_chart = px.line(
        df_aggregated_average_precipitation,
        x='date',
        y='precipitation_mm',
        color='continent',
        title='Average Precipitation',
        color_discrete_map=continent_colors
    )

    return average_precipitation_line_chart


def warmest_countries():
    # Top five warmest countries
    hot_colors = [
        'rgb(139, 0, 0)',
        'rgb(255, 0, 0)',
        'rgb(255, 69, 0)',
        'rgb(255, 140, 0)',
        'rgb(255, 204, 0)'
    ]

    df_top_ten_warmest_countries = pd.read_csv('./data/country_overall/top_5_warmest_countries.csv')
    top_five_warmest_countries_line_chart = px.line(
        df_top_ten_warmest_countries,
        x='date',
        y='max_temp_c',
        color='country',
        title='Top 5 Warmest Countries',
        color_discrete_sequence=hot_colors
    )
    top_five_warmest_countries_line_chart.update_layout(
        xaxis_title='Year',
        yaxis_title='Temperature [°C]',
        xaxis=dict(
            range=[start_day, end_day],
            fixedrange=False,
            constrain="domain",
            rangeslider=dict(visible=True),
            rangemode="normal",
        ),
        yaxis=dict(
            range=[-1, 60]
        )
    )

    return top_five_warmest_countries_line_chart


def coldest_countries():
    # Top five coldest countries
    cold_colors = [
        'rgb(173, 216, 230)',
        'rgb(0, 191, 255)',
        'rgb(135, 206, 235)',
        'rgb(70, 130, 180)',
        'rgb(0, 0, 139)',
    ]
    df_top_ten_coldest_countries = pd.read_csv('./data/country_overall/top_5_coldest_countries.csv')
    top_five_coldest_countries_line_chart = px.line(
        df_top_ten_coldest_countries,
        x='date',
        y='min_temp_c',
        color='country',
        title='Top 5 Coldest Countries',
        color_discrete_sequence=cold_colors,
    )
    top_five_coldest_countries_line_chart.update_layout(
        xaxis_title='Year',
        yaxis_title='Temperature in Celsius',
        xaxis=dict(
            range=[start_day, end_day],
            fixedrange=False,
            constrain="domain",
            rangeslider=dict(visible=True),
            rangemode="normal"
        ),
        yaxis=dict(
            range=[-41, 20]
        )
    )

    return top_five_coldest_countries_line_chart
