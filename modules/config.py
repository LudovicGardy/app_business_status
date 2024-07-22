import os

import toml
from dotenv import find_dotenv, load_dotenv


def load_configurations():
    """
    Charge uniquement les variables du fichier .env si celui-ci est présent.
    Si le fichier .env n'existe pas, charge toutes les variables d'environnement du système.
    """
    dotenv_path = find_dotenv(".env")

    if dotenv_path:
        # The .env file exists, load only its variables
        load_dotenv(dotenv_path)
        # Return the variables loaded from the .env
        return {
            key: os.environ[key]
            for key in os.environ
            if key in open(dotenv_path).read()
        }
    else:
        # The .env file does not exist, return all the system environment variables
        return dict(os.environ)


def load_toml_config(file_path):
    """
    Charge les configurations à partir d'un fichier .toml
    """
    try:
        with open(file_path, "r") as file:
            return toml.load(file).get("theme", {})
    except FileNotFoundError:
        return {}


def page_config():
    """
    Set the page configuration (title, favicon, layout, etc.)
    """
    env_variables = load_configurations()
    toml_config = load_toml_config(".streamlit/config.toml")

    page_dict = {
        "page_title": toml_config.get("page_title", "Mon Statut"),
        "sidebar_title": f"# {toml_config.get('sidebar_title', 'Mon Statut')}",
        "base": toml_config.get("base", "dark"),
        "page_icon": f'{env_variables.get("AWS_S3_URL", "")}/Sotis_AI_pure_darkbg_240px.ico',
        "page_logo": f'{env_variables.get("AWS_S3_URL", "")}/Sotis_AI_pure_darkbg_240px.png',
        "layout": toml_config.get("layout", "centered"),
        "initial_sidebar_state": toml_config.get("initial_sidebar_state", "auto"),
        "author": "Sotis AI",
        "markdown": """<style>.css-10pw50 {visibility:hidden;}</style>""",
        "page_description": """
        Une application conçue pour fournir des informations claires sur le choix entre deux structures juridiques françaises courantes : EURL et SASU.
        \n\nComparez le salaire net, les dividendes et l'impact financier global pour prendre une décision éclairée.
        \n\nDéveloppée par L. Gardy, Data Scientist indépendant chez [Sotis A.I.](https://www.sotisanalytics.com), cet outil offre une interface conviviale pour l'analyse financière.
        """,
    }

    return page_dict


def AWS_credentials():
    keys_list = ["AWS_S3_URL"]

    cred_dict = {}
    env_variables = load_configurations()

    # Check if all required keys exist and have a non-empty value
    try:
        for key in keys_list:
            value = env_variables.get(key.upper())
            if not value:
                raise ValueError(f"Missing or empty value for key: {key}")
            cred_dict[key] = value
    except ValueError as e:
        print(f"Configuration error: {e}")
        cred_dict = {}  # Reset cred_dict if any key is missing or empty

    return cred_dict
