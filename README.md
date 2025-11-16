# Bricolle Family project

## Installation (via docker)

1. Install [docker and docker compose](https://docs.docker.com/engine/install/)
2. Run

```shell
./deploy.sh
```

3. App is now ready and running on your computer, then create your first user (And other if you want more user inside
   your family)

```shell
docker compose exec web python manage.py createsuperuser
```

4. Lastly if you want to use the app name you'll have to import a name database. This one is the list of name given
   at least 500 times in the last 10 years in Île-de-France. You can adapt the initial database used of course or add
   other
   ones.

```shell
docker compose exec web python manage.py import_csv
```

5. Open: localhost:8000 and enjoy

---

## Modules list

1. Baby name

An app made with love by Zozette to help us pick the name of the baby.

2. Shopping list

An app to help you choose meal for the next week and then make the shopping list for you. It's shared with all your
household, and you edit it during your shopping session.

---

## Crontab
0 2 * * * /home/ubuntu/bricolle-family/backup_db.sh >> /home/ubuntu/bricolle-family/backup.log 2>&1
0 1 * * * /usr/bin/docker exec bricolle_web python manage.py update_deck_version >> /home/ubuntu/altered.log 2>&1
0 3 * * * /usr/bin/docker exec bricolle_web python manage.py compute_advised_price >> /home/ubuntu/altered.log 2>&1
0 3,15 * * * /home/ubuntu/Custom_projects/bricolle-family/scripts/manage_certs.sh renew >> /var/log/certbot-renew.log 2>&1
