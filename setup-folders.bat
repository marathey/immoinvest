@echo off

REM Create frontend structure
mkdir frontend
mkdir frontend\src
mkdir frontend\src\app

REM Create backend structure
mkdir backend
mkdir backend\src
mkdir backend\src\app

REM Create db structure
mkdir db

REM Create empty files
type nul > frontend\Dockerfile
type nul > frontend\.dockerignore
type nul > frontend\package.json
type nul > frontend\tailwind.config.js

type nul > backend\Dockerfile
type nul > backend\.dockerignore
type nul > backend\requirements.txt
type nul > backend\src\main.py

type nul > db\Dockerfile
type nul > db\init.sql

type nul > docker-compose.yml
type nul > .env

echo Project structure created successfully!
dir /s