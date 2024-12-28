import pandas as pd
import streamlit as st


def dataset_page():
    st.title("First Million Rows of the dataset used for this project")

    start_row, end_row = st.slider(
        "Subset of the dataset to include",
        min_value=0,
        max_value=1_000_000,
        value=(0, 100_000),
        step=10_000
    )

    df_chunk = load_data_chunk(start_row, end_row)
    st.dataframe(df_chunk)


@st.cache_data
def load_data_chunk(start_row: int, end_row: int):
    nrows = end_row - start_row + 1

    skip_rows = range(1, start_row + 1)

    df_chunk = pd.read_csv("./data/weather_compressed_csv.csv", skiprows=skip_rows, nrows=nrows, header=0)
    return df_chunk
