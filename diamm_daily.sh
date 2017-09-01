#!/usr/bin/env bash

OUTPUT_FILE_TSTAMP=`date "+%Y%m%d%H%M"`

# Backup the DIAMM SQL Database
/bin/sudo -u postgres /bin/pg_dumpall | /bin/gzip > /data/backups/diamm_db_backup_${OUTPUT_FILE_TSTAMP}.gz

# Vacuum the Postgres Database
/bin/sudo -u postgres /bin/vacuumdb --all --analyze