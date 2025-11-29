# Construire le container
docker build -t card-api .

# Lancer le container
docker run -p 8000:8000 card-api
