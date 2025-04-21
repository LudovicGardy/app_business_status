import streamlit as st

from src.config import page_config
from src.GUI.about import About
from src.GUI.home import Home
from src.GUI.ui_components import (
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
                st.Page(self.page_home, title="Accueil", icon="🏠"),
                st.Page(self.page_about, title="A propos", icon="ℹ️"),
            ]
        )
        pg.run()

    def page_home(self):
        Home()

    def page_about(self):
        About()


if __name__ == "__main__":
    app = App()
