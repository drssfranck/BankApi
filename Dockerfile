# Étape 1 : Choisir une image Python
FROM python:3.13-slim

# Étape 2 : Définir le répertoire de travail dans le container
WORKDIR /app

# Étape 3 : Copier les fichiers requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 4 : Copier le reste de l'application
COPY . .

# Étape 5 : Exposer le port sur lequel l'application va tourner
EXPOSE 8000

# Étape 6 : Commande pour lancer l'application FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
