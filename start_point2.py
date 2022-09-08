#!/usr/bin/python3

# ------------------------------ Описание ------------------------------

'''

Сценарий подставляет координаты начальной точки печати юбки или каймы,
в стартовый код вместо строки, содержащей аргумент --marker
G0 X20 Y20 Z0.0 F1200 ; MOVE TO START POSITION

Подробности в теме "Постобработка G-кода в PrusaSlicer" форума UNI:
https://uni3d.store/viewtopic.php?t=1041

Для работы сценария необходимо в профиле PrusaSlicer включить функцию:
Настройки печати - Выходные параметры - Подробный G-код.

Аргументы:
--marker 			Маркер для поиска строки перемещения в начальную позицию
--marker_retract	Маркер для поиска строки параметров ретракта прошивки (G10/G11)

'''

# -------------------------- Импорт библиотек --------------------------

import sys																					# Импорт библиотеки sys
import argparse																			# Импорт модуля обработки аргументов командной строки
from os import getenv

# ---------------------------- Аргуметны -------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('--marker', default='MOVE TO START POSITION', help='Маркер для поиска строки перемещения в начальную позицию')
parser.add_argument('--marker_retract', default='Set retract', help='Маркер для поиска строки параметров ретракта прошивки (G10/G11)')
parser.add_argument('file', help="Путь к g-коду", nargs="+")
args = parser.parse_args()

file_input=args.file[0]																	# Извлечение аргумента, путь к временному g-коду
if len(args.file) > 1:																	# Если аргументов 2,
	file_output=args.file[1]																# использовать 2-й аргумент для отладки
else:
	file_output=file_input																	# иначе записывать результат в исходный файл

# ----------------------- Извлечение параметров ------------------------

with open(file_input) as file:											# Открытие файла с g-кодом

	z_hop = ''
	speed = ''
	start_point_z = ''

	for line in file:																		# Построчная обработка файла

		if args.marker in line and (speed == '' or start_point_z == ''):	# Если строка содержит маркер
			print('\n' + line)
			move_old = line																# Сохраняем старую строку для последующей замены

			speed = line[line.find("F")+1:line.find(";")]						# Получаем часть строки от символа F до точки с запятой
			speed = speed.split(' ')[0]												# Разбиваем строку. Разделитель " ". Первый элемент - скорость F.
			print('speed = ' + str(speed))
			start_point_z = line[line.find("Z")+1:line.find(";")]				# Получаем часть строки от символа Z до точки с запятой
			start_point_z = start_point_z.split(' ')[0]							# Разбиваем строку. Разделитель " ". Первый элемент - координата Z.
			print('start_point_z = ' + str(start_point_z))

		if (args.marker_retract in line) and (z_hop == ''):					# Если строка содержит маркер ретракта
			print('\n' + line)
			z_hop = line[line.find("Z")+1:line.find(";")]
			z_hop = z_hop.split(' ')[0]
			z_hop = float(z_hop)
			print('z_hop = ' + str(z_hop))

		if ('move to first' in line):													# Поиск первой строки юбки или каймы
			move_to_first_point = line
			start_point_x = line[line.find("X")+1:line.find(";")]				# Получаем часть строки от символа X до точки с запятой
			start_point_x = start_point_x.split(' ')[0]							# Разбиваем строку. Разделитель " ". Первый элемент - координата X.
			
			start_point_y = line[line.find("Y")+1:line.find(";")]				# Получаем часть строки от символа Y до точки с запятой
			start_point_y = start_point_y.split(' ')[0]							# Разбиваем строку. Разделитель " ". Первый элемент - координата Y.

			break																				# Если первая команда юбки/каймы найдена, завершить обработку строк файла

# ------------------ Проверка полученных параметров --------------------
	
try:
	print(int(speed))
	print(float(start_point_x))
	print(float(start_point_y))
	print(float(start_point_z))
except:																						# При ошибке завершаем сценарий и выводим сообщение
	sys.exit("\n!!! Внимание !!!\nНе найдены координаты начала печати.")

# -------------------------- Изменение кода ----------------------------

# Новая строка перемещения в начальные координаты печати
move_new = "G1 X" + str(start_point_x) + " Y" + str(start_point_y) + " Z" + str(start_point_z) + " F" + str(speed) + " ; MOVE TO START POSITION POST-PROCESS\n"

with open (file_input, 'r') as file:												# Открываем оригинальный файл c g-кодом для чтения
	gcode = file.read()																	# Считываем содержимое файла в память

try:
	if z_hop > 0:																			# Если ретракт выполняется с опусканием стола
		height_first_layer = getenv('SLIC3R_FIRST_LAYER_HEIGHT')				# Добавить команду опускания для выборки люфта
		gcode = gcode.replace(args.marker_retract, args.marker_retract + "\n" + "G1 Z" + str(float(height_first_layer)+z_hop) + " ; z-hop", 1)
except:
	print("!!! Значение z-hop не найдено !!!")

gcode = gcode.replace(move_old, move_new, 1)										# Заменяем строку перемещения в начальные координаты печати
gcode = gcode.replace("G10 ; retract\n" + move_to_first_point + "G11 ; unretract\n", move_to_first_point, 1)	# Удаление ретракта вокруг начала каймы/юбки

with open (file_output, 'w') as file:												# Открываем файл c g-кодом для записи
	file.write(gcode)																		# Записываем результат в файл

# ======================================================================

# ------------------------------ Отладка -------------------------------
debug_text = ""																			# Формирование строки с данными отладки
debug_text = debug_text + "marker = " + args.marker + "\n"
debug_text = debug_text + "file_input = " + file_input + "\n"
debug_text = debug_text + "start_point_x = " + str(start_point_x) + "\n"
debug_text = debug_text + "start_point_y = " + str(start_point_y) + "\n"
debug_text = debug_text + "start_point_z = " + str(start_point_z) + "\n"
debug_text = debug_text + "speed = " + str(speed) + "\n"
debug_text = debug_text + "move_old = " + move_old + "\n"
debug_text = debug_text + "move_new = " + move_new + "\n"
debug_text = debug_text + "move_to_first_point = " + move_to_first_point + "\n"

print (debug_text)																		# Вывод информации отладки в терминал

# ======================================================================
