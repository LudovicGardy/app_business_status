import streamlit as st

from modules.GUI.home import IncomeCalculator
from modules.GUI.ui_components import init_page_config, display_sidebar, init_session_state
from modules.config import page_config 

class App:
    def __init__(self):

        init_page_config(page_config)
        init_session_state()

        with st.sidebar:
            display_sidebar(page_config)

        tabs = st.tabs(["Calculer le revenu", "Optimiser le revenu"])

        # Gestion des pages selon l'onglet sélectionné
        with tabs[0]:
            calc = IncomeCalculator()
        with tabs[1]:
            st.title("Page 2")
            st.write("Contenu de la Page 2 - Cette page pourrait inclure, par exemple, des calculatrices fiscales ou des analyses de responsabilité pour chaque structure juridique.")


if __name__ == '__main__':
    app = App()



