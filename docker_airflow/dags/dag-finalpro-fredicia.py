from datetime import datetime
import logging
from airflow import DAG
from airflow.models import Variable, Connection
from airflow.operators.python import PythonOperator

from modules.covid_scraper import CovidScraper
from modules.transformer import Transformer
from modules.connector import Connector

def func_get_data_from_api(**kwargs):
	#get data
	scraper = CovidScraper(Variable.get('url_covid_tracker'))
	data = scraper.get_data()
	print(data.info())
	
	#create connector
	get_conn = Connection.get_connection_from_secrets("Mysql")
	connector = Connector(get_conn.host,get_conn.login,get_conn.password,get_conn.schema,get_conn.port)
	engine_sql = connector.connect_mysql()
	
	try:
		p = "DROP table IF EXISTS covid_jabar"
		engine_sql.execute(p)
	except Exception as e:
		logging.error(e)
		
	#insert to mysql
	data.to_sql(con=engine_sql, name='covid_jabar', index=False)
	logging.info("INSERTED covid_jabar SUCCESSFULLY TO MYSQL")


def func_generate_dim(**kwargs):
	#create connector
	get_conn_mysql = Connection.get_connection_from_secrets("Mysql")
	get_conn_postgres = Connection.get_connection_from_secrets("Postgres")
	connector_mysql = Connector(get_conn_mysql.host,get_conn_mysql.login,get_conn_mysql.password,get_conn_mysql.schema,get_conn_mysql.port)
	engine_sql = connector_mysql.connect_mysql()

	connector_postgres = Connector(get_conn_postgres.host,get_conn_postgres.login,get_conn_postgres.password,get_conn_postgres.schema,get_conn_postgres.port)
	engine_postgres = connector_postgres.connect_postgres()

	generator_dim = Transformer(engine_sql,engine_postgres)
	generator_dim.create_dimension_district()
	generator_dim.create_dimension_province()
	generator_dim.create_dimension_case()

def func_insert_province_daily(**kwargs):
	get_conn_mysql = Connection.get_connection_from_secrets("Mysql")
	get_conn_postgres = Connection.get_connection_from_secrets("Postgres")
	connector_mysql = Connector(get_conn_mysql.host,get_conn_mysql.login,get_conn_mysql.password,get_conn_mysql.schema,get_conn_mysql.port)
	engine_sql = connector_mysql.connect_mysql()

	connector_postgres = Connector(get_conn_postgres.host,get_conn_postgres.login,get_conn_postgres.password,get_conn_postgres.schema,get_conn_postgres.port)
	engine_postgres = connector_postgres.connect_postgres()

	generator_province = Transformer(engine_sql,engine_postgres)
	generator_province.create_province_daily()
	

def func_insert_district_daily(**kwargs):
	get_conn_mysql = Connection.get_connection_from_secrets("Mysql")
	get_conn_postgres = Connection.get_connection_from_secrets("Postgres")
	connector_mysql = Connector(get_conn_mysql.host,get_conn_mysql.login,get_conn_mysql.password,get_conn_mysql.schema,get_conn_mysql.port)
	engine_sql = connector_mysql.connect_mysql()

	connector_postgres = Connector(get_conn_postgres.host,get_conn_postgres.login,get_conn_postgres.password,get_conn_postgres.schema,get_conn_postgres.port)
	engine_postgres = connector_postgres.connect_postgres()

	generator_district = Transformer(engine_sql,engine_postgres)
	generator_district.create_district_daily()

with DAG(
	dag_id='dag_finalpro_fredicia',
	start_date=datetime(2022,11,24),
	schedule_interval='0 0 * * *',
	catchup=False
) as dag:

	op_get_data_from_api = PythonOperator(
		task_id = 'get_data_from_api',
		python_callable = func_get_data_from_api
	)
	
	op_generate_dim = PythonOperator(
		task_id = 'generate_dim',
		python_callable = func_generate_dim
	)
	
	op_insert_province_daily = PythonOperator(
		task_id = 'insert_province_daily',
		python_callable = func_insert_province_daily
	)
	
	op_insert_district_daily = PythonOperator(
		task_id = 'insert_district_daily',
		python_callable = func_insert_district_daily
	)
	
op_get_data_from_api >> op_generate_dim
op_generate_dim >> op_insert_province_daily
op_generate_dim >> op_insert_district_daily