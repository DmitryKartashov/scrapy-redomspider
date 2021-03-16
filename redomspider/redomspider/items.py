# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy



class RedomItem(scrapy.Item):
	ev_type = scrapy.Field()
	ev_date = scrapy.Field()
	ev_time = scrapy.Field()
	ev_name = scrapy.Field()
	ev_place = scrapy.Field()
	ev_description = scrapy.Field()
	ev_image_path = scrapy.Field()