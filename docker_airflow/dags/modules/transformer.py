import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
import numpy as np

class Transformer():
	def _init__(self, engine_sql, engine_postgres):
		self.engine_sql = engine_sql
		self.engine_postgres = engine_postgres
		
	def get_data_from_api(self):
		sql = "SELECT * FROM covid_jabar"
		df = pd.read_sql(sql, con = self.engine_sql)
		print('GET DATA FROM MYSQL SUCCESS')
		return df
		
	def create_dimension_province(self):
		df = self.get_data_from_api()
		df_province_dim = df[['kode_prov', 'nama_prov']]
		df_province_dim = df_province_dim.rename(columns={'kode_prov':'province_id', 'nama_prov':'province_name'})
		df_province_dim = df_province_dim.drop_duplicates()
			
		try:
			p = "DROP TABLE IF EXISTS dim_province"
			self.engine_postgres.execute(p)
		except SQLAlchemyError as e:
			print(e)
			
		#insert to postgres
		df_province_dim.to_sql(con=self.engine_postgres, name='dim_province', index=False)
		print("INSERTED TO POSTGRES SUCCESSFULLY")
		
	def create_dimension_district(self):
		df = self.get_data_from_api()
		df_district_dim = df[['kode_kab', 'kode_prov', 'nama_kab']]
		df_district_dim = df_district_dim.rename(columns={'kode_kab':'district_id','kode_prov':'province_id', 'nama_kab':'district_name'})
		df_district_dim = df_district_dim.drop_duplicates()
		
		try:
			p = "DROP TABLE IF EXISTS dim_district"
			self.engine_postgres.execute(p)
		except SQLAlchemyError as e:
			print(e)
			
		#insert to postgres
		df_district_dim.to_sql(con=self.engine_postgres, name='dim_district', index=False)
		print("INSERTED TO POSTGRES SUCCESSFULLY")
		
	def create_dimension_case(self):
		df = self.get_data_from_api()
		column_start = ['suspect_diisolasi','suspect_discarded', 'suspect_meninggal',
			'closecontact_dikarantina', 'closecontact_discarded', 'closecontact_meninggal',
			'probable_diisolasi', 'probable_discarded', 'probable_meninggal',
			'confirmation_meninggal','confirmation_sembuh']
		column_end = ['id', 'status_name', 'status_detail', 'status']
		df_case_dim = df[column_start]
		df_case_dim = df_case_dim[:1]
		df_case_dim = df_case_dim.melt(var_name = "status", value_name = "total")
		df_case_dim = df_case_dim.drop_duplicates("status").sort_values("status")
		df_case_dim['id'] = np.arange(1, df_case_dim.shape[0]+1)
		df_case_dim[['status_name','status_detail']] = df_case_dim["status"].str.split('_', n = 1, expand = True)
		df_case_dim = df_case_dim[column_end]
		
		try:
			p = "DROP TABLE IF EXISTS dim_case"
			self.engine_postgres.execute(p)
		except SQLAlchemyError as e:
			print(e)
			
		#insert to postgres
		df_case_dim.to_sql(con=self.engine_postgres, name='dim_case', index=False)
		print("INSERTED TO POSTGRES SUCCESSFULLY")
		
	def create_province_daily(self):
		df = self.get_data_from_mysql()
		df_case_dim = self.create_dimension_case()
		
		column_start = ['tanggal', 'kode_kab', 'suspect_diisolasi','suspect_discarded', 'suspect_meninggal',
			'closecontact_dikarantina', 'closecontact_discarded', 'closecontact_meninggal',
			'probable_diisolasi', 'probable_discarded', 'probable_meninggal',
			'confirmation_meninggal','confirmation_sembuh']
		df_district_daily = df[column_start]
		df_district_daily = df_district_daily.rename(columns={'kode_kab':'district_id','tanggal':'date'})
		result_district_daily = pd.DataFrame(columns=['district_id', 'case_id', 'date', 'total'])

		for index, row in df_district_daily.iterrows():
			for col in df_district_daily.columns[3:]:
				data = [row['district_id'],df_case_dim.loc[df_case_dim['status']==col, 'id'].to_string(index=False),row['date'], row[col]]
				result_district_daily.loc[len(result_district_daily)] = data
				result_district_daily.insert(loc = 0, column = 'id', value = np.arange(1, result_district_daily.shape[0]+1))
				result_district_daily = result_district_daily.sort_values(['case_id', 'date', 'district_id'],ascending = [True, True, True])
		
		try:
			p = "DROP TABLE IF EXISTS district_daily"
			self.engine_postgres.execute(p)
		except SQLAlchemyError as e:
			print(e)
			
		#insert to postgres
		result_district_daily.to_sql(con=self.engine_postgres, name='district_daily', index=False)
		print("INSERTED TO POSTGRES SUCCESSFULLY")

	def create_district_daily(self):
		df = self.get_data_from_mysql()
		df_case_dim = self.create_dimension_case()
		
		column_start = ['tanggal', 'kode_prov', 'suspect_diisolasi','suspect_discarded', 'suspect_meninggal',
			'closecontact_dikarantina', 'closecontact_discarded', 'closecontact_meninggal',
			'probable_diisolasi', 'probable_discarded', 'probable_meninggal',
			'confirmation_meninggal','confirmation_sembuh']
		df_province_daily = df[column_start]
		df_province_daily = df_province_daily.rename(columns={'kode_prov':'province_id','tanggal':'date'})
		result_province_daily = pd.DataFrame(columns=['province_id', 'case_id', 'date', 'total'])

		for index, row in df_province_daily.iterrows():
			for col in df_province_daily.columns[3:]:
				data = [row['province_id'],df_case_dim.loc[df_case_dim['status']==col, 'id'].to_string(index=False),row['date'], row[col]]
				result_province_daily.loc[len(result_province_daily)] = data
				result_province_daily.insert(loc = 0, column = 'id', value = np.arange(1, result_province_daily.shape[0]+1))
				result_province_daily = result_province_daily.sort_values(['case_id', 'date', 'province_id'],ascending = [True, True, True])
		
		try:
			p = "DROP TABLE IF EXISTS province_daily"
			self.engine_postgres.execute(p)
		except SQLAlchemyError as e:
			print(e)
			
		#insert to postgres
		result_province_daily.to_sql(con=self.engine_postgres, name='province_daily', index=False)
		print("INSERTED TO POSTGRES SUCCESSFULLY")