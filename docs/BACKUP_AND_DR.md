# Backup and Disaster Recovery Plan

## Overview

This document outlines the backup and disaster recovery procedures for OmniFy Cloud Connect.

## Backup Strategy

### MongoDB Backups

**Frequency**: Daily at 2:00 AM UTC  
**Retention**: 30 days  
**Storage**: Local + S3 (if configured)

#### Automated Backups

Backups are performed automatically via Kubernetes CronJob:

```bash
# View backup job
kubectl get cronjob mongodb-backup -n omnify

# View backup job history
kubectl get jobs -n omnify -l job-name=mongodb-backup

# Manually trigger backup
kubectl create job --from=cronjob/mongodb-backup mongodb-backup-manual -n omnify
```

#### Manual Backup

```bash
# Using backup script
./ops/scripts/backup-mongodb.sh

# Or using kubectl exec
kubectl exec -it mongodb-pod -n omnify -- mongodump \
  --host=localhost:27017 \
  --username=admin \
  --password=$MONGODB_PASSWORD \
  --authenticationDatabase=admin \
  --db=omnify \
  --out=/backups/backup-$(date +%Y%m%d-%H%M%S)
```

### Redis Backups

Redis is primarily used for caching. For critical data:
- Enable Redis persistence (AOF + RDB)
- Regular snapshots to S3
- Consider Redis Cluster for high availability

### Application Data Backups

- Logs: Retained in Loki (30 days)
- Metrics: Retained in Prometheus (15 days)
- User uploads: Stored in S3 with versioning

## Restore Procedures

### MongoDB Restore

#### From Local Backup

```bash
# Extract and restore
./ops/scripts/restore-mongodb.sh /backups/mongodb/backup-20240101-020000.tar.gz
```

#### From S3 Backup

```bash
# Download from S3
aws s3 cp s3://omnify-backups/mongodb/backup-20240101-020000.tar.gz /tmp/

# Restore
./ops/scripts/restore-mongodb.sh /tmp/backup-20240101-020000.tar.gz
```

#### Point-in-Time Recovery

For point-in-time recovery:
1. Restore latest full backup
2. Apply oplog replay (if available)
3. Verify data integrity

### Full System Restore

1. **Restore Infrastructure**
   ```bash
   # Apply Kubernetes manifests
   kubectl apply -f ops/k8s/
   ```

2. **Restore MongoDB**
   ```bash
   ./ops/scripts/restore-mongodb.sh <backup-file>
   ```

3. **Restore Redis** (if needed)
   ```bash
   # Restore from snapshot
   redis-cli --rdb /backups/redis/dump.rdb
   ```

4. **Verify Services**
   ```bash
   # Check health endpoints
   curl https://api.omnify.com/health
   ```

## Disaster Recovery Scenarios

### Scenario 1: Database Corruption

**Recovery Steps**:
1. Stop application services
2. Restore from latest backup
3. Verify data integrity
4. Restart services
5. Monitor for issues

**RTO**: 1 hour  
**RPO**: 24 hours (last backup)

### Scenario 2: Complete Infrastructure Loss

**Recovery Steps**:
1. Provision new infrastructure
2. Restore Kubernetes cluster
3. Restore MongoDB from S3 backup
4. Restore application configuration
5. Verify all services
6. Update DNS if needed

**RTO**: 4-6 hours  
**RPO**: 24 hours

### Scenario 3: Data Center Outage

**Recovery Steps**:
1. Failover to secondary region (if configured)
2. Restore from cross-region backups
3. Update DNS to point to new region
4. Monitor and verify services

**RTO**: 2-4 hours  
**RPO**: 24 hours

## Testing

### Backup Verification

Test backups monthly:

```bash
# Test restore to staging environment
./ops/scripts/restore-mongodb.sh <backup-file> --target-env=staging
```

### DR Drill

Conduct DR drills quarterly:
1. Simulate disaster scenario
2. Execute recovery procedures
3. Verify system functionality
4. Document lessons learned

## Monitoring

- Backup job success/failure alerts
- Backup storage usage monitoring
- Restore operation logging
- Backup integrity checks

## Best Practices

1. **3-2-1 Rule**: 3 copies, 2 different media, 1 offsite
2. **Encryption**: Encrypt backups at rest
3. **Testing**: Regularly test restore procedures
4. **Documentation**: Keep procedures up to date
5. **Automation**: Automate backup and restore processes

## Contacts

- **Backup Administrator**: [Contact Info]
- **DR Coordinator**: [Contact Info]
- **On-Call Engineer**: [Contact Info]

## Revision History

- 2025-01-XX: Initial version

