#!/bin/bash
#python3 app.py
uwsgi --http 127.0.0.1:8000 --wsgi-file app.py --callable run_exporter --disable-logging --enable-threads
