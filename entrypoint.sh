#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python << END
import sys
import time
from os import getenv

import psycopg

suggest_unrecoverable_after = 30
start = time.time()

user=getenv('POSTGRES_USER')
password=getenv('POSTGRES_PASSWORD')
host=getenv('DATABASE_HOST')
port=getenv('DATABASE_PORT')
name=getenv('POSTGRES_DB')
url = f"postgres://{user}:{password}@{host}:{port}/{name}"
while True:
    try:
        con = psycopg.connect(conninfo=url)
    except psycopg.OperationalError as error:
        sys.stderr.write("Waiting for PostgreSQL to become available...\n")

        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write("  This is taking longer than expected. The following exception may be indicative of an unrecoverable error: '{}'\n".format(error))
    else:
        con.close()
        break
    time.sleep(1)
END

./opt/manage.sh migrate "something";
cd /opt/project && alembic upgrade head;

>&2 echo 'PostgreSQL is available'

tail -f /var/log/cron.log &

exec "$@"
