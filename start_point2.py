#!/usr/bin/env python3

# ------------------------------ Описание ------------------------------

'''

Сценарий подставляет координаты начальной точки печати юбки или каймы,
в стартовый код вместо строки, содержащей аргумент --marker
G0 X20 Y20 Z0.0 F1200 ; MOVE TO START POSITION

Подробности в теме "Постобработка G-кода в PrusaSlicer" форума UNI:
https://uni3d.store/viewtopic.php?t=1041

Для работы сценария необходимо в профиле PrusaSlicer включить функцию:
Настройки печати - Выходные параметры - Подробный G-код.

При использовании аргумента --debug сохраняется файл отладки.
'''

# -------------------------- Импорт библиотек --------------------------

import sys																# Иморт модуля sys
																		# sys.argv - список аргументов командной строки, которые причастны к сценарию
																		# sys.argv[0] - путь к файлу сценария
																		# sys.argv[-1] - путь к файлу с g-кодом (временнный, во временном каталоге)

from os import getenv													# Импорт модуля для получения значений переменных окружения
																		# Необходимо для получения параметров профиля PrusaSlicer

import argparse															# Импорт модуля обработки аргументов командной строки

# ======================================================================

# ----------------------------- Сценарий -------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('--marker', default='MOVE TO START POSITION', help='Маркер для поиска строки перемещения в начальную позицию')
parser.add_argument('--debug', action='store_true', help='Сохраняет файл отладки')
parser.add_argument('file', help="Путь к g-коду", nargs="+")
args = parser.parse_args()

file_input = str(sys.argv[-1])											# PrusaSlicer последним аргументом передаёт путь к временному файлу с g-кодом

with open(file_input) as file:											# Открытие файла с g-кодом

	for line in file:													# Построчная обработка файла

		if args.marker in line:											# Если строка содержит маркер
			move_old = line												# Сохраняем старую строку для последующей замены

			speed = line[line.find("F"):line.find(";")]					# Получаем часть строки от символа F до точки с запятой
			speed = speed.split(' ')[0]									# Разбиваем строку. Разделитель " ". Первый элемент - скорость F.

			start_point_z = line[line.find("Z"):line.find(";")]			# Получаем часть строки от символа Z до точки с запятой
			start_point_z = start_point_z.split(' ')[0]					# Разбиваем строку. Разделитель " ". Первый элемент - координата Z.

		if "move to first skirt point" in line or "move to first brim point" in line:	# Поиск первой строки юбки или каймы
			move_skirt_brim = line
			start_point_x = line[line.find("X"):line.find(";")]			# Получаем часть строки от символа X до точки с запятой
			start_point_x = start_point_x.split(' ')[0]					# Разбиваем строку. Разделитель " ". Первый элемент - координата X.
			
			start_point_y = line[line.find("Y"):line.find(";")]			# Получаем часть строки от символа Y до точки с запятой
			start_point_y = start_point_y.split(' ')[0]					# Разбиваем строку. Разделитель " ". Первый элемент - координата Y.

			break														# Если первая команда юбки/каймы найдена, завершить обработку строк файла


# Новая строка перемещения в начальные координаты печати
move_new = "G1 " + str(start_point_x) + " " + str(start_point_y) + " " + str(start_point_z) + " " + str(speed) + " ; MOVE TO START POSITION POST-PROCESS\n"

with open (file_input, 'r') as file:									# Открываем оригинальный файл c g-кодом для чтения
	gcode = file.read()													# Считываем содержимое файла в память

gcode = gcode.replace(move_old, move_new, 1)							# Заменяем строку перемещения в начальные координаты печати
gcode = gcode.replace("G10 ; retract\n" + move_skirt_brim + "G11 ; unretract\n", move_skirt_brim, 1)	# Удаление ретракта вокруг начала каймы/юбки

with open (file_input, 'w') as file:									# Открываем файл c g-кодом для записи
	file.write(gcode)													# Записываем результат в файл

# ======================================================================

# ------------------------------ Отладка -------------------------------
debug_text = ""															# Формирование строки с данными отладки
debug_text = debug_text + "marker = " + args.marker + "\n"
debug_text = debug_text + "file_input = " + file_input + "\n"
debug_text = debug_text + "start_point_x = " + str(start_point_x) + "\n"
debug_text = debug_text + "start_point_y = " + str(start_point_y) + "\n"
debug_text = debug_text + "start_point_z = " + str(start_point_z) + "\n"
debug_text = debug_text + "speed = " + str(speed) + "\n"
debug_text = debug_text + "move_old = " + move_old + "\n"
debug_text = debug_text + "move_new = " + move_new + "\n"
debug_text = debug_text + "move_skirt_brim = " + move_skirt_brim + "\n"

debug_text = debug_text + "LAYER_HEIGHT = " + str(getenv('SLIC3R_LAYER_HEIGHT')) + "\n" # Получение параметра из профиля PrusaSlicer

print (debug_text)														# Вывод информации отладки в терминал

if args.debug:
	with open(file_input + ".log", "w") as file:						# Открыть/создать файл
		file.write(debug_text)											# Сохранение данных отладки в файл

# ======================================================================
