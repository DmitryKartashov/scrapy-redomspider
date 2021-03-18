# -*- coding: utf-8 -*- 

import scrapy
import sys
import os
from datetime import datetime, timedelta

# здесь будет искаться модуль 'items' и 'eventspider_settings'
sys.path.append('../')
from items import RedomItem
import eventspider_settings as ev_settings

class RedomSpider1(scrapy.Spider):
	name = 'redomspider1'
	download_delay = 0.3
	randomize_download_delay = True

	def __init__(self, category=None, *args, **kwargs):
		super(RedomSpider1, self).__init__(*args, **kwargs)

		self.allowed_event_types = ('parties','concerts','theater','sport','shows','exhibitions')
		self.main_domain = ev_settings.MAIN_DOMAIN
		self.main_directory = ev_settings.MAIN_DIRECTORY
		self.dir_images = ev_settings.DIR_IMAGES
		self.dir_datasets = ev_settings.DIR_DATASETS

		self.cur_name_of_image = 0

		self.dir_images_day = self.create_img_dir()
		self.start_date, self.end_date, self.ev_types = self.get_meta()


	def create_img_dir(self):
		args = sys.argv[-1]
		meta = args.split('/')[-1]
		dir_name = meta.split('.')[0]
		try: # создаем папку для сохранения наборов данных
			os.mkdir(self.dir_datasets)
		except: pass

		try: # создаем папку для сохранения картинок
			os.mkdir(self.dir_images)
		except:pass
		dir_images_day = self.dir_images+'IMAGES_'+dir_name

		try: # создаем папку для сохранения картинок событий этого дня
			os.mkdir(dir_images_day)
		except:pass
		return dir_images_day

	def get_meta(self):
		'''
		Syear_Smonth_Sday-Eyear_Emonth_Eday-type1_type2_..._tipeN(or ALL).json(or csv)

		По названию создаваемого файла определяет начальную и конечную даты
		событий, а так же типы событий, предназначенных дл парсинга.
		'''
		try:
			args = sys.argv[-1]
			meta = args.split('/')[-1]
			meta = meta.split('.')[0]
			start_date,end_date,ev_types = meta.split('-')

			start_date = start_date.split('_')
			start_date = datetime(int(start_date[0]),int(start_date[1]),int(start_date[2]))

			end_date = end_date.split('_')
			end_date = datetime(int(end_date[0]),int(end_date[1]),int(end_date[2]))

			ev_types = ev_types.split('_')
			if len(ev_types) and ev_types[0] == 'ALL':
				ev_types = self.allowed_event_types
			else:
				ev_types = [ev_t for ev_t in ev_types if ev_t in self.allowed_event_types]
		except Exception:
			start_date = datetime.today()
			end_date = datetime.today()
			ev_types = self.allowed_event_types

		return start_date, end_date, ev_types

	def start_requests(self):
		'''
		Нужно пройти по всем типам событий за указанный промежуток времени.
		'''
		zero_giver = lambda s: '0'*(len(s)==1)+s
		# /{event_type}/{year-month-day}/
		template_page_events_for_day_url = 'https://www.redomm.ru/afisha/{}/{}/'
		template_date = '{}-{}-{}'

		delta = timedelta(hours = 24)

		for i in range((self.end_date-self.start_date).days+1):
			date = self.start_date + i*delta
			ev_date = template_date.format(date.year,
										zero_giver(str(date.month)),
										zero_giver(str(date.day)))
			for ev_type in self.ev_types:
				page_events_for_day_url = template_page_events_for_day_url.format(ev_type,ev_date)
				yield scrapy.Request(url = page_events_for_day_url,
									callback = self.parse_events_page,
									cb_kwargs = {'ev_type':ev_type,
													'ev_date':ev_date})

	def parse_events_page(self, response, ev_type, ev_date):
		'''
		Сюда приходит код страницы со списком событий.
		Дальше ищем все ссылки на события и переходим по ним.
		'''
		def get_places(event_places):
			i,j = 0,3
			places = []
			cur = ''
			while j <= len(event_places):
				for s in event_places[i:j]:
					s = s.strip().strip('/ ')
					cur+=s+'|'
				places.append(cur[:-1].strip('|'))
				cur = ''
				i+=3
				j+=3
			return places

		is_empty_page_xpath = '//div[@class = "content_block"]//text()'
		event_urls_xpath = '//table[@class="schedule schedule-events"]//tr/td[1]/a/@href'
		event_places_xpath = '//table[@class="schedule schedule-events"]//tr/td\
							[@class="schedule_place  schedule_row-indented "]//text()'
		event_times_xpath = '//table[@class="schedule schedule-events"]//tr/td[@class=\
							"schedule_time_wrap schedule_row-indented"]//span[@class="schedule_time__text"]/text()'

		is_empty_page_text = response.xpath(is_empty_page_xpath).getall()
		if 'По заданным критериям событий не найдено' in is_empty_page_text:
			event_urls = []
			event_places = []
			event_times = []
		else:
			event_urls = response.xpath(event_urls_xpath).getall()
			event_places = response.xpath(event_places_xpath).getall()
			event_times = response.xpath(event_times_xpath).getall()

			event_places = get_places(event_places)
		for obj in zip(event_urls,event_places,event_times):
			ev_time = obj[2]
			ev_place = obj[1]
			one_event_url = self.main_domain+obj[0]
			if 'https://www.redomm.ru/afisha/place/' not in one_event_url:#костыль
				yield scrapy.Request(url = one_event_url,
									callback = self.parse_one_event,
									cb_kwargs = {'ev_type':ev_type,
													'ev_date':ev_date,
													'ev_time':ev_time,
													'ev_place':ev_place})

	def parse_one_event(self,response, ev_type, ev_date, ev_time, ev_place):
		def get_fusion(ev_description):
			res = ''
			for desc in ev_description:
				res = res + desc +'|'
			return res[:-1].strip()

		ev_name_xpath = '//h1[@class="title-inline title-no_indent"]/text()'
		ev_description_xpath = '//div[@class = "content_block"]/div[@class = "text"]/p/text()'
		ev_image_binary_xpath = '//div[@class="content_block"]/div[@class="once_responsive_photo"]/a[@id="poster"]/@href'

		ev_name = response.xpath(ev_name_xpath).get().strip()
		ev_description = response.xpath(ev_description_xpath).getall()
		ev_image_url = response.xpath(ev_image_binary_xpath).get()

		ev_description = get_fusion(ev_description)

		yield scrapy.Request(url = ev_image_url, callback = self.parse_image,
								cb_kwargs = {'ev_type':ev_type,
													'ev_date':ev_date,
													'ev_time':ev_time,
													'ev_place':ev_place,
													'ev_name':ev_name,
													'ev_description':ev_description})

	def parse_image(self, response, ev_type, ev_date, ev_time, ev_place, ev_name, ev_description):
		ev_image_rel_path = self.dir_images_day+'/'+str(self.cur_name_of_image)+'.jpg'

		ev_image_abs_path = os.path.abspath(ev_image_rel_path)

		# увеличиваем имя следующей картинки
		self.cur_name_of_image += 1

		with open(ev_image_abs_path, 'wb') as f:
			f.write(response.body)

		
		item = RedomItem({'ev_type':ev_type,
						'ev_date':ev_date,
						'ev_time':ev_time,
						'ev_place':ev_place,
						'ev_name':ev_name,
						'ev_description':ev_description,
						'ev_image_path':ev_image_abs_path})
		yield item