start:
	poetry run python manage.py runserver

migrate:
	poetry run python manage.py migrate

migrations:
	poetry run python manage.py makemigrations

console:
	poetry run python manage.py console
