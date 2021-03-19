# -*- coding: utf-8 -*- 

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import psycopg2
import sys
sys.path.add('../')

import eventspider_settings as es

class RedomspiderPipeline:
	def open_spider(self, spider):
		self.con = psycopg2.connect(
				database = es.DB_NAME,
				user = es.DB_USER,
				password = es.DB_PASSWORD,
				host = es.DB_HOST,
				port = es.DB_PORT)

	def close_spider(self, spider):
		self.con.close()

	def process_item(self, item, spider):
		sql_insert_template = '''
			insert into event
			(title,date_event,time_event,location,description)
			values('{}',{},{},{},'{}')
		'''
		return item
