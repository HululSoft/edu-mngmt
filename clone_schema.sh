#!/bin/bash
set -euo pipefail

DB_NAME="school_management"
SOURCE_SCHEMA="public"
DEST_SCHEMA="school_dev"
DB_USER="postgres"
DB_HOST="153.92.223.114"
DB_PORT="5400"

export PGPASSWORD=admin
echo "🔄 Cloning schema '$SOURCE_SCHEMA' to '$DEST_SCHEMA' in database '$DB_NAME'..."

pg_dump16='/opt/homebrew/opt/postgresql@16/bin/pg_dump'
psql16='/opt/homebrew/opt/postgresql@16/bin/psql'

# start with schema migration. Example: /opt/homebrew/opt/postgresql@16/bin/pg_dump -h 153.92.223.114 -p 5400 -U postgres --schema-only school_management -n public > school_management_schema.sql
echo "Dumping schema..."
$pg_dump16 -h $DB_HOST -p $DB_PORT -U $DB_USER --schema-only $DB_NAME -n $SOURCE_SCHEMA > source_schema.sql

# then data... Example: /opt/homebrew/opt/postgresql@16/bin/pg_dump -h 153.92.223.114 -p 5400 -U postgres --data-only school_management -n public > school_management_data.sql
echo "Dumping data..."
$pg_dump16 -h $DB_HOST -p $DB_PORT -U $DB_USER --data-only $DB_NAME -n $SOURCE_SCHEMA > source_data.sql


# Now, modify the dumped SQL files to change the schema name. Example: sed -i '' 's/public/school_dev/g' school_management_schema.sql
sed -i '' "s/$SOURCE_SCHEMA/$DEST_SCHEMA/g" source_schema.sql
sed -i '' "s/$SOURCE_SCHEMA/$DEST_SCHEMA/g" source_data.sql

# drop the destination schema if it exists to avoid conflicts.
echo "Dropping existing destination schema if it exists..."
$psql16 -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME -c "DROP SCHEMA IF EXISTS $DEST_SCHEMA CASCADE;"

# Create the destination schema in the database. Example: psql -U postgres school_management -h 153.92.223.114 -p 5400 < school_management_schema.sql
echo "Creating destination schema..."
$psql16 -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME < source_schema.sql
# Load the modified data into the new schema. Example: psql -U postgres school_management -h 153.92.223.114 -p 5400 < school_management_data.sql
echo "Loading data into destination schema..."
$psql16 -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME < source_data.sql

echo "✅ Clone complete!"
