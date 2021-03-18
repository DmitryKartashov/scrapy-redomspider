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
4. Запускайте паука следующим образом:
		scrapy runspider eventspider.py -o ../../../datasets/YYYY_M_D-YYYY_M_D-ALL.json

	Где YYYY_M_D-YYYY_M_D  -  начало и конец временного интервала, внутри
								которого будет проводиться поиск событий

	ALL  -  это типы событий, которые нас интересуют.
			Вместо ALL можно через нижнее подчеркивание перечислить
			типы из списка: 
				('parties','concerts','theater','sport','shows','exhibitions')
	Например: 
		../../../datasets/2021_3_10-2021_3_24-concerts_shows_theater.csv

5. Фотографии событий сохранятся в папке images,
	датасет будет загружен в папку datasets.

## Структура проекта

scrapy-redomspider/
	.gitignore
	README.md
	datasets/ #создастся после первого запуска
	images/ #создастся после первого запуска
	redomspider/
		scrapy.cfg
		redomspider/
			spiders/
				eventspider.py
			eventspider_settings.py
			items.py
			middlewares.py
			pipelines.py
			settings.py
