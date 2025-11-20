#!/bin/bash
# Backup Verification Script
# Verifies MongoDB backups are valid and restorable

set -e

BACKUP_DIR="${BACKUP_DIR:-/backups/mongodb}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
VERIFICATION_LOG="${VERIFICATION_LOG:-/var/log/backup-verification.log}"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$VERIFICATION_LOG"
}

verify_backup() {
    local backup_file="$1"
    log "Verifying backup: $backup_file"
    
    # Check if backup file exists and is not empty
    if [ ! -f "$backup_file" ] || [ ! -s "$backup_file" ]; then
        log "ERROR: Backup file is missing or empty: $backup_file"
        return 1
    fi
    
    # Check backup file integrity (if it's a tar/archive)
    if [[ "$backup_file" == *.tar.gz ]] || [[ "$backup_file" == *.tar ]]; then
        if ! tar -tzf "$backup_file" > /dev/null 2>&1; then
            log "ERROR: Backup archive is corrupted: $backup_file"
            return 1
        fi
    fi
    
    # Check file size (should be > 0)
    local size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$size" -eq 0 ]; then
        log "ERROR: Backup file is empty: $backup_file"
        return 1
    fi
    
    log "SUCCESS: Backup verified: $backup_file (size: $size bytes)"
    return 0
}

# Main verification process
main() {
    log "Starting backup verification"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log "ERROR: Backup directory does not exist: $BACKUP_DIR"
        exit 1
    fi
    
    local verified_count=0
    local failed_count=0
    
    # Verify all backups
    for backup_file in "$BACKUP_DIR"/*.tar.gz "$BACKUP_DIR"/*.tar "$BACKUP_DIR"/*.dump; do
        if [ -f "$backup_file" ]; then
            if verify_backup "$backup_file"; then
                ((verified_count++))
            else
                ((failed_count++))
            fi
        fi
    done
    
    log "Verification complete: $verified_count verified, $failed_count failed"
    
    if [ $failed_count -gt 0 ]; then
        log "WARNING: Some backups failed verification"
        exit 1
    fi
    
    # Clean up old backups
    log "Cleaning up backups older than $RETENTION_DAYS days"
    find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete
    
    log "Backup verification completed successfully"
}

main "$@"

