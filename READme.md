# build
    docker-compose up --build

# v novém terminálu

## Vytvoření tabulek
    docker-compose exec web python manage.py migrate

## Naplnění dummy daty
    docker-compose exec web python manage.py seed_data

### app dostupná na localhost:8000

### superuser pro POST, UPDATE, DEL: localhost:8000/admin
    docker-compose exec web python manage.py createsuperuser -> pokyny
