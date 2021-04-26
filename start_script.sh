#!/bin/bash

cd "${0%/*}" || return
source env/bin/activate
python3 noti.py
