import streamlit as st
from page.dataset_page import dataset_page
from page.global_page import global_page
from page.search_page import search_page


def main():
    st.set_page_config(layout="wide")

    page_global, page_search, page_dataset = st.tabs(["Global", "Search", "Dataset"])

    with st.container():
        with page_dataset:
            dataset_page()

        with page_global:
            global_page()

        with page_search:
            search_page()


if __name__ == "__main__":
    main()
