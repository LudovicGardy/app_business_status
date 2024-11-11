from typing import Callable

import streamlit as st


def display_sidebar(page_config: Callable):
    logo_path = page_config().get("page_logo")
    desired_width = 60

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(logo_path, width=desired_width)
    with col2:
        st.write(page_config().get("sidebar_title"))

    st.caption(page_config().get("page_description"))
    st.divider()


def init_session_state():
    if "type_societe" not in st.session_state:
        st.session_state["type_societe"] = 0
    if "choix_fiscal" not in st.session_state:
        st.session_state["choix_fiscal"] = 0
    if "selected_tab" not in st.session_state:
        st.session_state["selected_tab"] = 0
    if "best_trial" not in st.session_state:
        st.session_state["best_trial"] = {}
    if "salaire_annuel_sansCS_avantIR" not in st.session_state:
        st.session_state["salaire_annuel_sansCS_avantIR"] = 10000
    if "proportion_du_resultat_versee_en_dividende" not in st.session_state:
        st.session_state["proportion_du_resultat_versee_en_dividende"] = 100
    if "charges_deductibles" not in st.session_state:  
        st.session_state["charges_deductibles"] = 32000


def init_page_config(
    page_config: Callable,
):  ### Must be called before any other st. function
    st.set_page_config(
        page_title=page_config().get("page_title"),
        page_icon=page_config().get("page_icon"),
        layout=page_config().get("layout"),
        initial_sidebar_state=page_config().get("initial_sidebar_state"),
    )
