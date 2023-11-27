from sqlalchemy import create_engine

class Connector():
	def __init__(self,host, user, password,	db,	port):
		self.host = host
		self.user = user
		self.password = password
		self.db = db
		self.port = port
		
	def connect_mysql(self):
		db_params = {
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "database": self.db
        }
		print("Connecting to MySQL")
		conn_mysql = f'mysql+mysqlconnector://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}'
		print(conn_mysql)
		engine = create_engine(conn_mysql)
		return engine
	
	def connect_postgres(self):
		db_params = {
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "database": self.db
        }
		print("Connecting to PostgreSQL")
		conn_postgre = f'postgresql+psycopg2://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}'
		engine = create_engine(conn_postgre)
		return engine