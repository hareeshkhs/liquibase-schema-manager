# Liquibase Schema Manager

A lightweight tool to manage schema changes and automate versioning for database projects using Liquibase, GitHub Actions, and Docker.

---

## 🚀 Features

- Supports schema management using Liquibase for multiple databases.
- Currently Supports PostgreSQL. (Future datastores release - Snowflake)
- Customised liquibase module as pyquibase to encapsulate liquibase setup, supports easy version upgrades.
- Automatically bumps semantic versions (`major`, `minor`, `patch`, `prerelease`) based on commit messages
- Builds and pushes Docker images to GitHub Container Registry (GHCR)
- Uses GitHub Actions to lint, test, version, and deploy
- Supports email notifications for deployment status, logs, trace, and database high-level details.

---

## 📁 Project Structure
```
liquibase-schema-manager/
│
├── .github/workflows/               # Github actions files
│   ├── ci-cd.yaml                   # cicd job code for code version management, push image to Github Container registry
│   └── deploy.yaml                  # action file to deploy a version into datastores
│
├── postgres/                        # Postgres datastore DDLs
│   ├── core/                        # Core schema DDLs
│   └── merchant_template/           # Merchant template schema DDLs
│
├── pyquibase/                       # Pyquibase module files
│   ├── db-connectors/               # Datastores versions jar files. ex: postgres, snowflake, etc.
│   └── liquibase/                   # Liquibase version jar file
│   └── liquibase_executor.py        # Execute function utilized in pyquibase.py function
│   └── pyquibase.py                 # Pyquibase Function code.py
│
├── .env                             # env variables
├── .gitignore                       # Git ignore rules
├── README.md                        # Project overview
├── Dockerfile                       # Container configuration for deploying the application
├── bump_version.py                  # Script to increment version numbers (major/minor/patch)
├── calculate_version.py             # Logic for determining the current version
├── config.py                        # configuration settings and constants
├── connector.py                     # Handles connections to external services/databases
├── email_notifications.py           # Email sending functionality and templates
├── main.py                          # Entry point and primary application logic
├── requirements.py                  # Manages project dependencies and requirements
├── version.py                       # Current version info
```
---

## Table of Contents
1. [Deploying Schema](#deploying-schema-with-docker)
2. [Usage](#usage)
   - [Local development setup](#local-development-setup)
   - [Installing Requirements for Local Development](#installing-requirements-for-local-development)
   - [Configuring credentials](#configuring-credentials)
   - [Deploying a fresh schema](#deploying-a-fresh-schema-locally)
   - [Adding new migrations](#updatingchanging-the-schema)
   - [Upgrading the schema](#upgrading-the-schema)
   - [Adding a new schema](#adding-a-new-schema)
3. [Miscellaneous](#miscellaneous)
   - [Checking Schema Version](#checking-the-version-of-the-schema-on-a-database)

## Deploying Schema With Docker
- Set the Docker image
```shell script
docker login ghcr.io -u $username --password-stdin
docker pull ghcr.io/hareeshkhs/liquibase-schema-manager:$SM_TAG
```
- To deploy schemas, set the DB credentials and the schemas in the following command and execute 
```
docker run --name "$CONTAINER_NAME" \ 
-e AVAILABLE_SCHEMAS="v9/l0, v9/l1, v9/l2, v9/l3"
-e POSTGRES_HOST=HOST \ 
-e PORT=PORT \ 
-e POSTGRES_DB=DB_NAME \ 
-e POSTGRES_USER=USERNAME \ 
-e POSTGRES_PASSWORD=PASSWORD \ 
-e EMAIL_APP_PASSCODE=EMAIL_APP_PASSCODE \
ghcr.io/hareeshkhs/liquibase-schema-manager:$SM_TAG
```
- Check that the output of the following query matches `$SM_TAG`.
```
SELECT tag FROM db_logs.databasechangelog ORDER BY dateexecuted DESC LIMIT 1;
```
## Usage

### Local development setup
- Clone the remote repository
```
git clone https://github.com/hareeshkhs/liquibase-schema-manager.git
```
- Create a sub-branch with name prefix as feature/{branch_name}, and checkout into the branch
```
git checkout -b feature/patient_table_change_020525
```

### Installing Requirements for Local Development
- Install the virtualenv
```
pip install virtualenv
```
- Create a virtual environment
```
python3 -m venv venv
```
- Activate the virtual environment and install requirements
```
source venv/bin/activate
pip install -r requirements.txt 
```
### Configuring credentials
- Schema Manager retrieves config from environment variables or from a [.env](.env) file
- Required environment variables:
```
AVAILABLE_SCHEMAS="postgres/core,postgres/merchant_template"              # list of schemas to deploy
POSTGRES_HOST=database_host                 # DB Host on which deployment is to happen
POSTGRES_DB=db_name                         # Name of the database on which deployment is to happen
PORT=5432                                   # DB Port
POSTGRES_USER=user_name                     # Username to login to the DB with
POSTGRES_PASSWORD=strong_password           # Password to login to the DB with
```

### Deploying a fresh schema locally
- Make sure schemas configured in `AVAILABLE_SCHEMAS` DO NOT exist on the database
- Make sure the user has the necessary privileges.
- Execute the following command to deploy the schemas
```shell script
python3 main.py
```
- Check that the schemas have been deployed.
- Check that the following tables exist in the database in the `public` schema
    - databasechangelog
    - databasechangeloglock 
- Check that the output of the following query matches `__version__` in [version.py](version.py)
```shell script
SELECT tag FROM db_logs.databasechangelog ORDER BY dateexecuted DESC LIMIT 1;
```

### Updating/changing the schema
- Create a new "changelog" file in the folder that corresponds to the schema you wish to update or change.
- This file contains the `ALTER/CREATE` SQL statements to update or change the schema.
- For example
```shell script
touch postgres/core/2025_05_02_15_45_00_patient_table_changes.sql
```
- Note the format of the name. It is `YYYY_MM_DD_HH_MM_SS_{Change_Title}.sql`
- Always put the latest date and time for the file name. If the file is committed and pushed to the repo at a later date, then rename the file name to match the date and time.
- The file extension must be `.sql`
- The file must begin with the following line:
```
--liquibase formatted sql
```
- The changeset tag must be of the form: `owner:id`
- Recommended `id` is [Unix Epoch Time](https://www.epochconverter.com/) in seconds at which the SQL is written.
- The changeset tag must be put for each SQL statement.
- If the SQL statements exceed more than one line, add a `splitStatements:false`
- For more help on creating changelog files, follow [here](https://docs.liquibase.com/concepts/basic/sql-format.html)
- Make sure to refer to tables, views, other entities with their full names, i.e. `"SCHEMA"."ENTITY_NAME"`
- Make sure schemas configured in `AVAILABLE_SCHEMAS` exist on the database
- Set the credentials of the test DB in [.env](.env)
- Execute the following command to upgrade the schemas:
```shell script
python3 main.py
```
- Check that the output of the following query on the test DB matches `__version__` in [version.py](version.py)
```
SELECT tag FROM db_logs.databasechangelog ORDER BY dateexecuted DESC LIMIT 1;
```
- Commit the changes made to a `feature/` branch and raise a merge request to `master`.

### Upgrading the schema
- Make sure schemas configured in `AVAILABLE_SCHEMAS` exist on the database
- Check that the following tables exist in the database in the `db_logs` schema
    - databasechangelog
    - databasechangeloglock 
- Note the output of the following query:
```
SELECT tag FROM db_logs.databasechangelog ORDER BY dateexecuted DESC LIMIT 1;
```
- Note the version described as `__version__` in [version.py](version.py)
- Execute the following command to upgrade the schemas:
```shell script
python3 main.py
```
- Check that the output of the following query matches `__version__` in [version.py](version.py)
```
SELECT tag FROM db_logs.databasechangelog ORDER BY dateexecuted DESC LIMIT 1;
```

### Adding a new schema
- Create a new folder with the name of the schema
- For example:
```shell script
mkdir postgres/merchant/core
```
- Follow the steps in [Updating/changing the schema](#updatingchanging-the-schema) to create a new changelog file in this folder
- The first two changesets should be:
```shell script
--changeset AUTHOR:ID splitStatements:false
CREATE SCHEMA core;

--changeset AUTHOR:ID splitStatements:false
SET SEARCH_PATH TO core;
```
- Follow the steps in [Updating/changing the schema](#updatingchanging-the-schema) to add more statements in the changelog file.
- Commit the changes made to a `feature/` branch and raise a merge request to `master`.
## Miscellaneous
### Checking the version of the schema on a database
- Check that the output of the following query matches `__version__` in [version.py](version.py)
```
SELECT tag FROM db_logs.databasechangelog ORDER BY dateexecuted DESC LIMIT 1;
```
