#!/usr/bin/env bash

# Grab the details from a configuration file.
source .backups

OUTPUT_FILE_TSTAMP=`date "+%Y%m%d%H%M"`

# Backup the DIAMM SQL Database
/bin/sudo -u postgres /bin/pg_dumpall | /bin/gzip > ${LOCAL_BACKUP_PATH}/diamm_db_backup_${OUTPUT_FILE_TSTAMP}.gz

# Upload the backup to the remote server
curl -X PUT --data-binary @"${LOCAL_BACKUP_PATH}/diamm_db_backup_${OUTPUT_FILE_TSTAMP}.gz" -u "${BACKUP_USER}:${BACKUP_PASS}" "${BACKUP_SERVER}/diamm_db_backup_${OUTPUT_FILE_TSTAMP}.gz"

# Vacuum the Postgres Database
/bin/sudo -u postgres /bin/vacuumdb --all --analyze