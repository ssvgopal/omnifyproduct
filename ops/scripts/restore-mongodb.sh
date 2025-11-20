#!/bin/bash
# MongoDB Restore Script for OmniFy
# Usage: ./restore-mongodb.sh <backup-file.tar.gz>

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <backup-file.tar.gz>"
  exit 1
fi

BACKUP_FILE="$1"
MONGODB_HOST="${MONGODB_HOST:-mongodb-service}"
MONGODB_PORT="${MONGODB_PORT:-27017}"
MONGODB_USER="${MONGODB_USER:-admin}"
MONGODB_PASSWORD="${MONGODB_PASSWORD}"
MONGODB_DATABASE="${MONGODB_DATABASE:-omnify}"
RESTORE_DIR="/tmp/mongodb-restore"

# Extract backup
echo "Extracting backup..."
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Find the backup directory
BACKUP_DIR=$(find "$RESTORE_DIR" -type d -name "backup-*" | head -1)
if [ -z "$BACKUP_DIR" ]; then
  BACKUP_DIR=$(find "$RESTORE_DIR" -type d -name "$MONGODB_DATABASE" | head -1)
fi

if [ -z "$BACKUP_DIR" ]; then
  echo "Error: Could not find backup directory in archive"
  exit 1
fi

# Confirm restore
echo "WARNING: This will restore database '$MONGODB_DATABASE' from backup."
echo "This will OVERWRITE existing data!"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Restore cancelled"
  exit 0
fi

# Restore database
echo "Restoring MongoDB..."
mongorestore \
  --host="$MONGODB_HOST:$MONGODB_PORT" \
  --username="$MONGODB_USER" \
  --password="$MONGODB_PASSWORD" \
  --authenticationDatabase=admin \
  --db="$MONGODB_DATABASE" \
  --drop \
  "$BACKUP_DIR/$MONGODB_DATABASE"

# Cleanup
rm -rf "$RESTORE_DIR"

echo "Restore completed successfully"

