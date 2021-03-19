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
		self.cur = self.con.cursor()

	def close_spider(self, spider):
		self.con.close()

	def process_item(self, item, spider):
		'''(title,date_event,time_event,location,description)'''
		sql_insert_event_template = '''
			WITH ev_key AS
				(INSERT INTO event(title,date_event,time_event,location,description)
							VALUES('{title}','{date_event}','{time_event}',{location},'{description}')
							RETURNING id),
				cat_key AS
				(SELECT id FROM categories
							WHERE category = '{category}'),
				_ AS
				(INSERT INTO category_event(category_id,event_id)
						SELECT cat_key.id, ev_key.id
						FROM cat_key,ev_key RETURNING id),
				med_key AS
				(SELECT id FROM media_type WHERE type = 'image')
				INSERT INTO event_media(url,type_id,event_id)
					SELECT '{url}',med_key.id,ev_key.id
					FROM med_key, ev_key;
		'''

"""
					{'ev_type':ev_type,
						'ev_date':ev_date,
						'ev_time':ev_time,
						'ev_place':ev_place,
						'ev_name':ev_name,
						'ev_description':ev_description,
						'ev_image_path':ev_image_abs_path}
"""


		sql_insert_event = sql_insert_event_template.format(title = item['ev_name'],
															date_event = item['ev_date'],
															time_event = item['ev_time'],
															location = {'loc_name':item['place']},
															description = item['ev_description'],
															category = item['ev_type'],
															url = item['ev_image_path'])

		self.cur.execute(sql_insert_event)
		self.cur.commit()
		return item
