#!/usr/bin/bash

python3 manage.py migrate --check

if [[ $? == 0 ]]; then
    python3 manage.py migrate
fi

python3 .\manage.py collectstatic -c --no-input
exec "$@"
