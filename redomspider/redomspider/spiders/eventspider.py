import scrapy
import sys
import os
from datetime import datetime, timedelta

# здесь будет искаться модуль 'items'
sys.path.append('D:/home/projects/galaxy/git-scraping-redom/redomspider/redomsoider/')

from items import RedomItem

import eventspider_settings as ev_settings

class RedomSpider1(scrapy.Spider):
	name = 'redomspider1'
	download_delay = 0.3
	randomize_download_delay = True

	allowed_event_types = ('parties','concerts','theater','sport','shows','exhibitions')
	main_domain = ev_settings.MAIN_DOMAIN

	# здесь будет создаваться папка 'images', в которую бдут размещаться все скачанные картинки в 
	# соответствующих подпапках
	main_directory = ev_settings.MAIN_DIRECTORY

	def create_img_dir(self):
		args = sys.argv[-1]
		dir_name = args.split('.')[0]
		try:
			os.mkdir(self.main_directory+'images/')
		except:pass
		image_dir = self.main_directory+'images/'+'IMAGES_'+dir_name
		try:
			os.mkdir(image_dir)
		except:pass
		return image_dir

	def get_meta(self):
		'''
		Syear_Smonth_Sday-Eyear_Emonth_Eday-type1_type2_..._tipeN(or ALL).json(or csv)

		По названию создаваемого файла определяет начальную и конечную даты
		событий, а так же типы событий, предназначенных дл парсинга.
		'''
		try:
			args = sys.argv[-1]
			meta = args.split('.')[0]
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
		self.image_dir = self.create_img_dir()
		start_date,end_date,ev_types = self.get_meta()
		delta = timedelta(hours = 24)
		# /{event_type}/{year-month-day}/
		template_page_events_for_day_url = 'https://www.redomm.ru/afisha/{}/{}/'
		template_date = '{}-{}-{}'
		for i in range((end_date-start_date).days+1):
			date = start_date + i*delta
			ev_date = template_date.format(date.year,
										zero_giver(str(date.month)),
										zero_giver(str(date.day)))
			for ev_type in ev_types:
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
		ev_image_path = self.image_dir+'/'+ev_name+'.jpg'
		with open(ev_image_path, 'wb') as f:
			f.write(response.body)

		if os.path.exists(ev_image_path):
			item = RedomItem({'ev_type':ev_type,
							'ev_date':ev_date,
							'ev_time':ev_time,
							'ev_place':ev_place,
							'ev_name':ev_name,
							'ev_description':ev_description,
							'ev_image_path':ev_image_path})
			yield item