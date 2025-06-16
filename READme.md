# build
docker-compose up --build

# nový terminál

## Vytvoření tabulek
docker-compose exec web python manage.py migrate

## Naplnění daty
docker-compose exec web python manage.py seed_data
