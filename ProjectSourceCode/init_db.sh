#!/bin/bash

# DO NOT PUSH THIS FILE TO GITHUB
# This file contains sensitive information and should be kept private

# TODO: Set your PostgreSQL URI - Use the External Database URL from the Render dashboard
PG_URI="postgresql://exampleuser:zJkUcXEmcD6EjVggmeGuyncBYBPY0dJz@dpg-d7gki05ckfvc73fue73g-a.oregon-postgres.render.com/users_db_6qhg"

# Execute each .sql file in the directory
for file in init_data/*.sql; do
    echo "Executing $file..."
    psql $PG_URI -f "$file"
done