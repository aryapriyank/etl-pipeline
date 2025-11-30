# ETL Pipeline

ETL Pipeline using Apache Airflow with PostgreSQL and Open-Meteo API.

## Setup

### PgAdmin Configuration

1. Go to `localhost:5050`
2. Click on **Add Server**
3. Under **General** tab:
   - **Name**: Give any name (e.g., `postgres_db`)
4. Under **Connection** tab:
   - **Hostname**: Get the IP address of the postgres container by running the following command:
     ```bash
     docker inspect <container_id>
     ```
     (The values below are defined in the docker-compose file for postgres)
   - **Port**: `5432`
   - **Database**: `airflow`
   - **Username**: `airflow`
   - **Password**: `airflow`

### Airflow Connection Settings

#### 1. PostgreSQL Connection (`postgres_default`)

- **Connection ID**: `postgres_default`
- **Connection Type**: `Postgres`
- **Host**: PostgreSQL container name (e.g., `etl-pipeline-postgres-1`)
- **Login**: `airflow`
- **Password**: `airflow`
- **Port**: `5432`
- **Database**: `airflow`

#### 2. Open-Meteo API Connection (`open_meteo_api`)

- **Connection ID**: `open_meteo_api`
- **Connection Type**: `HTTP`
- **Host**: `https://api.open-meteo.com`
