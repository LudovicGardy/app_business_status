import streamlit as st

from modules.config import page_config
from modules.GUI.home import IncomeCalculator
from modules.GUI.ui_components import (
    display_sidebar,
    init_page_config,
    init_session_state,
)


class App:
    def __init__(self):
        init_page_config(page_config)
        init_session_state()

        with st.sidebar:
            display_sidebar(page_config)

        pg = st.navigation(
            [
                st.Page(self.page1, title="Accueil", icon="🏠"),
                st.Page(self.page2, title="A propos", icon="ℹ️"),
            ]
        )
        pg.run()

    def page1(self):
        tabs = st.tabs(["Optimiser le revenu"])  # , "Voir les résultats"])
        with tabs[0]:
            calc = IncomeCalculator()

    def page2(self):
        st.write("Not implemented tey")


if __name__ == "__main__":
    app = App()
