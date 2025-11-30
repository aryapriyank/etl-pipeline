from datetime import datetime
import json, requests

from airflow import DAG
from airflow.sdk import task
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


DAG_ID = 'etl_weather_data'
LATITUDE = 40.7128
LONGITUDE = -74.0060
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'open_meteo_api'
API_ENDPOINT = f"/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"

# Host = 'https://api.open-meteo.com'
# Query Endpoint = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true"


with DAG(
    dag_id = DAG_ID,
    start_date=datetime(2025, 11, 30),
    schedule='@daily',
    catchup=False
) as dags:

    @task
    def fetch_weather_data():
        # Fetch weather data from the Open-Meteo API
        # Using HttpHook to make the API request for weather data
        http_hook = HttpHook(method='GET', http_conn_id=API_CONN_ID)
        response = http_hook.run(API_ENDPOINT)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        
        return response.json()


    @task
    def transform_weather_data(weather_data):
        # Transform the fetched weather data
        current_weather = weather_data['current_weather']
        transformed_data = {
            'latitude': weather_data['latitude'],
            'longitude': weather_data['longitude'],
            'temperature': current_weather['temperature'],
            'windspeed': current_weather['windspeed'],
            'winddirection': current_weather['winddirection'],
            'weathercode': current_weather['weathercode']         
        }
        return transformed_data


    create_weather_data_table = SQLExecuteQueryOperator(
        task_id='create_weather_data_table',
        conn_id = POSTGRES_CONN_ID,
        sql = 'sql/weather_data_schema.sql',
    )
    

    @task
    def load_weather_data(transformed_data):
        # Load the transformed data into Postgres
        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        insert_sql = """
            INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        postgres_hook.run(insert_sql, autocommit=True, parameters=(
            transformed_data['latitude'],
            transformed_data['longitude'],
            transformed_data['temperature'],
            transformed_data['windspeed'],
            transformed_data['winddirection'],
            transformed_data['weathercode']
        ))


    # Define task dependencies
    weather_data = fetch_weather_data()
    transformed_data = transform_weather_data(weather_data)
    create_weather_data_table >> load_weather_data(transformed_data)
