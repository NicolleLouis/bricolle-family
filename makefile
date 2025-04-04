start:
	poetry run python manage.py runserver

migrate:
	poetry run python manage.py migrate

migrations:
	poetry run python manage.py makemigrations

test:
	poetry run pytest

console:
	poetry run python manage.py shell
