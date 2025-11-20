#!/bin/bash
# MongoDB Backup Script for OmniFy
# Run daily via cron or Kubernetes CronJob

set -e

# Configuration
BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=30
MONGODB_HOST="${MONGODB_HOST:-mongodb-service}"
MONGODB_PORT="${MONGODB_PORT:-27017}"
MONGODB_USER="${MONGODB_USER:-admin}"
MONGODB_PASSWORD="${MONGODB_PASSWORD}"
MONGODB_DATABASE="${MONGODB_DATABASE:-omnify}"
S3_BUCKET="${S3_BUCKET:-omnify-backups}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating MongoDB backup..."
mongodump \
  --host="$MONGODB_HOST:$MONGODB_PORT" \
  --username="$MONGODB_USER" \
  --password="$MONGODB_PASSWORD" \
  --authenticationDatabase=admin \
  --db="$MONGODB_DATABASE" \
  --out="$BACKUP_DIR/backup-$DATE"

# Compress backup
echo "Compressing backup..."
tar -czf "$BACKUP_DIR/backup-$DATE.tar.gz" -C "$BACKUP_DIR" "backup-$DATE"
rm -rf "$BACKUP_DIR/backup-$DATE"

# Upload to S3 (if configured)
if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
  echo "Uploading to S3..."
  aws s3 cp "$BACKUP_DIR/backup-$DATE.tar.gz" "s3://$S3_BUCKET/mongodb/backup-$DATE.tar.gz"
fi

# Cleanup old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "backup-*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: backup-$DATE.tar.gz"

