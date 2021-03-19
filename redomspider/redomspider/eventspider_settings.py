# -*- coding: utf-8 -*- 

# Доступ к корневой папке проекта из папки с пауками
MAIN_DIRECTORY = '../../../'

# Доступ к папке, в которую будут скачиваться
# картинки событий
DIR_IMAGES = MAIN_DIRECTORY + 'images/'

# Если не в базу данных, то в эту
# директорию бует заливаться
# вся спарсенная информация
DIR_DATASETS = MAIN_DIRECTORY + 'datasets/'

# Домен, в котором будет выполняться парсинг
MAIN_DOMAIN = 'https://www.redomm.ru'

# ИНФОРМАЦИЯ О БАЗЕ ДАННЫХ 
	#(в нее парсер буде заливать информацию)
DB_NAME = 'galaxy'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'
DB_HOST ='::1'
DB_PORT = '5432'