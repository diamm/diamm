#!/bin/bash

NAME="diamm"                            # name of the application
VIRTUAL_ENV="/srv/webapps/diamm/denv"   # name of virtual_env directory
DJANGODIR="/srv/webapps/diamm"               # Django project directory
SOCKFILE="/var/run/diamm/diamm.sock"                # we will communicate using this unix socket
USER=www                         # the user to run as
GROUP=www                       # the group to run as
NUM_WORKERS=5                           # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=diamm.settings   # which settings file should Django use
DJANGO_WSGI_MODULE=diamm.wsgi    # WSGI module name

echo "Starting $NAME"

# Activate the virtual environment
cd $DJANGODIR
source ${VIRTUAL_ENV}/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
#RUNDIR=$(dirname $SOCKFILE)
#test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ${VIRTUAL_ENV}/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --timeout 300
