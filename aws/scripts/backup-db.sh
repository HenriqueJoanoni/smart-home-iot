#!/bin/bash

###############################################
# Database Backup Script
###############################################

set -e

BACKUP_DIR="/opt/smart-home-iot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

mkdir -p "$BACKUP_DIR"

echo "📦 Creating database backup..."

docker exec smart_home_timescaledb_prod pg_dump \
    -U ${POSTGRES_USER:-smarthome_user} \
    -d ${POSTGRES_DB:-smarthome_db} \
    -F c -b -v -f /tmp/backup.dump

docker cp smart_home_timescaledb_prod:/tmp/backup.dump "$BACKUP_FILE"

echo "✅ Backup saved to: $BACKUP_FILE"

# Keep only last 7 backups
find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +7 -delete

echo "🧹 Old backups cleaned"