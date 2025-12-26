start:
	poetry run python manage.py runserver

migrate:
	poetry run python manage.py migrate

migrations:
	poetry run python manage.py makemigrations

test:
	rm -f test_db.sqlite3
	poetry run pytest --create-db

console:
	poetry run python manage.py shell

collectstatic:
	poetry run python manage.py collectstatic
