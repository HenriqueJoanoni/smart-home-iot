#!/bin/bash

###############################################
# Database Restore Script
###############################################

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /opt/smart-home-iot/backups/db_backup_20260111_120000.sql"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will restore the database from backup!"
echo "Backup file: $BACKUP_FILE"
read -p "Continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo "📥 Copying backup to container..."
docker cp "$BACKUP_FILE" smart_home_timescaledb_prod:/tmp/restore.dump

echo "🔄 Restoring database..."
docker exec smart_home_timescaledb_prod pg_restore \
    -U ${POSTGRES_USER:-smarthome_user} \
    -d ${POSTGRES_DB:-smarthome_db} \
    -c -v /tmp/restore.dump

echo "✅ Database restored successfully!"