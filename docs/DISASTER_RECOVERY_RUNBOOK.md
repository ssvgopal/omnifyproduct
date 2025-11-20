# 🚨 Disaster Recovery Runbook

**Version**: 1.0  
**Last Updated**: January 2025  
**Owner**: DevOps Team

---

## 📋 Overview

This runbook provides step-by-step procedures for disaster recovery scenarios for OmniFy Cloud Connect.

---

## 🔴 CRITICAL CONTACTS

- **On-Call Engineer**: [Contact Info]
- **Database Admin**: [Contact Info]
- **Infrastructure Lead**: [Contact Info]
- **Security Team**: [Contact Info]

---

## 🎯 RECOVERY OBJECTIVES

- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour (last backup)
- **Data Retention**: 30 days of backups

---

## 📦 BACKUP STRATEGY

### **Automated Backups**
- **Frequency**: Daily at 2:00 AM UTC
- **Location**: `/backups/mongodb/`
- **Retention**: 30 days
- **Verification**: Automated daily verification

### **Backup Types**
1. **Full Database Backup**: Complete MongoDB dump
2. **Incremental Backup**: Changes since last full backup
3. **Configuration Backup**: Application configs, secrets

---

## 🚨 DISASTER SCENARIOS

### **Scenario 1: Database Corruption**

**Symptoms**:
- Database connection errors
- Data inconsistency reports
- Application errors

**Recovery Steps**:

1. **Assess Damage**
   ```bash
   # Check database status
   mongosh --eval "db.adminCommand('ping')"
   
   # Check for corruption
   mongosh --eval "db.runCommand({validate: 'collection_name'})"
   ```

2. **Stop Application**
   ```bash
   # Stop all services
   docker compose -f ops/docker/docker-compose.prod.yml down
   ```

3. **Restore from Backup**
   ```bash
   # List available backups
   ls -lh /backups/mongodb/
   
   # Restore most recent backup
   ./ops/scripts/restore-mongodb.sh /backups/mongodb/backup-YYYY-MM-DD.tar.gz
   ```

4. **Verify Restoration**
   ```bash
   # Verify data integrity
   mongosh --eval "db.stats()"
   
   # Check critical collections
   mongosh --eval "db.campaigns.countDocuments()"
   ```

5. **Restart Services**
   ```bash
   docker compose -f ops/docker/docker-compose.prod.yml up -d
   ```

6. **Post-Recovery Checks**
   - Verify application health
   - Check critical endpoints
   - Monitor error logs

---

### **Scenario 2: Complete System Failure**

**Symptoms**:
- All services down
- Infrastructure unavailable
- No access to systems

**Recovery Steps**:

1. **Assess Infrastructure**
   - Check cloud provider status
   - Verify network connectivity
   - Check DNS resolution

2. **Restore Infrastructure**
   ```bash
   # Restore from infrastructure as code
   terraform apply -auto-approve
   
   # Or restore from backup
   kubectl apply -f ops/k8s/
   ```

3. **Restore Database**
   ```bash
   # Restore MongoDB
   ./ops/scripts/restore-mongodb.sh <backup-file>
   ```

4. **Restore Application**
   ```bash
   # Deploy application
   docker compose -f ops/docker/docker-compose.prod.yml up -d
   
   # Or Kubernetes
   helm upgrade omnify ./ops/helm/
   ```

5. **Verify System**
   - Health checks
   - Smoke tests
   - Monitor logs

---

### **Scenario 3: Data Loss**

**Symptoms**:
- Missing data
- Incomplete records
- User reports

**Recovery Steps**:

1. **Identify Affected Data**
   - Review logs
   - Check audit trails
   - Identify time range

2. **Restore from Backup**
   ```bash
   # Restore specific collection
   mongorestore --db=omnify --collection=campaigns \
     /backups/mongodb/backup-YYYY-MM-DD/campaigns.bson
   ```

3. **Verify Data Integrity**
   - Compare record counts
   - Check data consistency
   - Validate relationships

4. **Notify Users**
   - Communicate data restoration
   - Provide timeline
   - Monitor for issues

---

## 🔧 RESTORATION PROCEDURES

### **Full Database Restore**

```bash
#!/bin/bash
# Full database restore procedure

BACKUP_FILE="$1"
MONGO_URL="${MONGO_URL:-mongodb://localhost:27017}"
DB_NAME="${DB_NAME:-omnify_cloud}"

# Stop application
docker compose -f ops/docker/docker-compose.prod.yml stop backend

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp/restore

# Restore database
mongorestore --uri="$MONGO_URL" \
  --db="$DB_NAME" \
  --drop \
  /tmp/restore/

# Verify restore
mongosh "$MONGO_URL/$DB_NAME" --eval "db.stats()"

# Restart application
docker compose -f ops/docker/docker-compose.prod.yml start backend
```

### **Partial Restore (Collection Level)**

```bash
# Restore specific collection
mongorestore --uri="$MONGO_URL" \
  --db="$DB_NAME" \
  --collection="campaigns" \
  /backups/mongodb/backup-YYYY-MM-DD/campaigns.bson
```

---

## ✅ POST-RECOVERY CHECKLIST

- [ ] All services running
- [ ] Database accessible
- [ ] Health checks passing
- [ ] Critical endpoints responding
- [ ] No error logs
- [ ] Data integrity verified
- [ ] Users notified
- [ ] Incident report created
- [ ] Root cause analysis scheduled

---

## 📊 MONITORING & ALERTING

### **Key Metrics to Monitor**
- Database connection status
- Backup success/failure
- Disk space usage
- Application health

### **Alerts**
- Backup failure
- Database corruption
- Disk space < 20%
- Service downtime > 5 minutes

---

## 🔄 REGULAR TESTING

### **Monthly DR Drill**
1. Test backup restoration
2. Verify recovery procedures
3. Update runbook if needed
4. Document lessons learned

### **Quarterly Full DR Test**
1. Simulate complete failure
2. Execute full recovery
3. Measure RTO/RPO
4. Update procedures

---

## 📝 INCIDENT LOG

| Date | Incident | Resolution Time | Notes |
|------|----------|----------------|-------|
| | | | |

---

**Last Updated**: January 2025

