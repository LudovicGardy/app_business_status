# Utiliser une image Python de base (3.8-slim-buster)
FROM python:3.11-slim-buster

# Définir le dossier de travail
WORKDIR /app_business_status

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du code source
COPY . .

# Exécuter votre script Python
CMD ["streamlit", "run", "main.py"]
