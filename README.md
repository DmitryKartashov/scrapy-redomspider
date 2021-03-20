# Паук для парсинга сайта http://www.redomm.ru
----------------------------------------------

## Инструкция по запуску на своей машине

0. установите Scrapy: 
		pip install scrapy
1. Откройте терминал в той директории, в которой хотите разместить проект
2. Инициализируйте пустой репозиторий: 
		git init
3. Клонируйте репозиторий:
		git clone https://github.com/DmitryKartashov/scrapy-redomspider.git

4. В файле eventspider_settings.py настроить следующие параметры
	- DB_NAME = 'galaxy'
	- DB_USER = 'postgres'
	- DB_PASSWORD = 'admin'
	- DB_HOST ='::1'
	- DB_PORT = '5432'
	host и port можно узнать, введя в SQL shell следующие команды:
			- \c db_name //тут вместо db_name вставить название базы данных
			- \conninfo
5. Запускайте паука следующим образом:
		scrapy crawl redomspider -a start_date="YYYY_M_D" -a end_date="YYYY_M_D" -a types="type1_type2_typeN"

	Где start_date, end_date  -  начало и конец временного интервала, внутри
								которого будет проводиться поиск событий

	types  -  это типы событий, которые нас интересуют.
			Если types="ALL", то будут искаться все типы событий.
			Вместо ALL можно через нижнее подчеркивание перечислить
			типы из списка: 
				('parties','concerts','theater','sport','shows','exhibitions')
	Например: 
		scrapy crawl redomspider -a start_date="2021_2_1" -a end_date="2021_2_28" -a types="parties_shows"

6. Фотографии событий сохранятся в папке images

## Структура проекта

- scrapy-redomspider/
	- .gitignore
	- README.md
	- datasets/ #создастся после первого запуска
	- images/ #создастся после первого запуска
	- redomspider/
		- scrapy.cfg
		- redomspider/
			- spiders/
				- eventspider.py
			- eventspider_settings.py
			- items.py
			- middlewares.py
			- pipelines.py
			- settings.py
