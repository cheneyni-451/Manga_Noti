#!/bin/bash

cd "${0%/*}" || return
source env/bin/activate
exec python3 noti.py
