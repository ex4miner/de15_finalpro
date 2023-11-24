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
		engine = create_engine(
                f'mysql+pymysql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}/{db_params["database"]}')
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
		engine = create_engine(
                f'postgresql+psycopg2://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}/{db_params["database"]}')
		return engine