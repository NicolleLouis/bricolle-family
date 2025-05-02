#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H-%M")
BACKUP_DIR=./backups
FILENAME=$BACKUP_DIR/pg_dump_$DATE.sql

mkdir -p $BACKUP_DIR

docker compose exec -T db pg_dump -U postgres -d postgres > $FILENAME

find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete