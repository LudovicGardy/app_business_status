## 🗂️ Structure du projet

Le projet est organisé selon la structure suivante :

```
app_business_status/
│
├── src/                # Code source principal de l'application
│   ├── __init__.py
│   ├── config.py       # Configuration centrale et constantes
│   ├── impot_revenu.py # Calculs pour l'impôt sur le revenu
│   ├── impot_societes.py # Calculs pour l'impôt sur les sociétés
│   ├── societe.py      # Modélisation des structures juridiques
│   └── GUI/            # Interface utilisateur Streamlit
│       ├── __init__.py
│       ├── about.py    # Page "À propos"
│       ├── home.py     # Page d'accueil et logique principale UI
│       └── ui_components.py # Composants réutilisables de l'UI
│
├── main.py             # Point d'entrée de l'application Streamlit
├── pyproject.toml      # Dépendances et configuration Python (utilisé par uv)
├── docker-compose.yaml # Configuration pour lancer l'app avec Docker
├── Dockerfile          # Image Docker pour déploiement
├── .env                # Variables d'environnement (non versionnées)
├── images/             # Images utilisées dans la documentation/app
├── notebooks/          # Notebooks Jupyter pour analyses/tests
├── tests/              # Tests unitaires
│   └── unit/           # Tests pour les modules principaux
├── config/             # (Optionnel) Configurations additionnelles
└── README.md           # Ce fichier
```

**Résumé des principaux dossiers/fichiers :**
- `src/` : contient tout le code métier et l’UI.
- `main.py` : lance l’application Streamlit.
- `notebooks/` : pour l’exploration, les tests et la visualisation.
- `tests/` : tests unitaires pour garantir la fiabilité du code.
- `images/` : ressources graphiques pour la doc ou l’UI.
- `pyproject.toml` et `.env` : gestion des dépendances et des variables d’environnement.
- `docker-compose.yaml` et `Dockerfile` : pour le déploiement et l’exécution dans des environnements isolés.
