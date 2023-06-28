@echo off
title Chat Server
cd /d/Applications/server/CloudEmptying
call activate CloudEmptying
python flaskapp.py
python wsserver.py
