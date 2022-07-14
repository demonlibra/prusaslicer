#!/usr/bin/python3

# ----------------------------- Описание -------------------------------

'''

Сценарий активирует обдув для слоёв с мостами.

Подробности в теме "Постобработка G-кода в PrusaSlicer" форума UNI:
https://uni3d.store/viewtopic.php?t=1041

В профилях PrusaSlicer необходимо:
- Включить функцию "Подробный G-код"
- Задать "Скорость вентилятора при печати мостов" в профиле прутка.

Для отладки выполнить в терминале:
python3 overhang_perimeters.py <"исходный_файл_с_g-кодом"> <"файл_для_сохранения_результата">

'''

# -------------------------- Импорт библиотек --------------------------

import sys																# Импорт библиотеки sys
import argparse															# Импорт модуля обработки аргументов командной строки
from os import getenv													# Импорт модуля для получения значений переменных окружения

# ---------------------------- Аргуметны -------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('file', help="Путь к g-коду", nargs="+")			# Задание путей к файлам с g-кодом
args = parser.parse_args()

file_input=args.file[0]													# Извлечение аргумента, путь к временному g-коду
if len(args.file) > 1:													# Если аргументов 2,
	file_output=args.file[1]											 # использовать 2-й аргумент для отладки
else:
	file_output=file_input												 # иначе записывать результат в исходный файл

# ------------------------ Параметры нарезки ---------------------------

try:
	bridge_fan_speed = int(getenv('SLIC3R_BRIDGE_FAN_SPEED'))			# Получение скорости вентилятора из слайсера
except Exception:
	bridge_fan_speed = 255

print("bridge_fan_speed = " + str(bridge_fan_speed))

# ------------------- Маркеры для поиска типа линий --------------------

marker_layer_number = "move to next layer ("
marker_bridge = "bridge"
marker_fan = "M106 S"

marker_stop = "; stop printing object"
marker_layer_change = ";LAYER_CHANGE"

# -------------------------- Изменение кода ----------------------------

with open(file_input) as file:											# Открываем файл для чтения
	lines = file.readlines()												# Заносим все строки файла в список

index = 0																# Счётчик строк
layer_number = 0														# Счётчик номера обрабатывамой строки
layer_number_line = 0													# Номер строки указателя слоя
flag_bridge_layer = False												# Указатель слоя с мостами

for line in lines:														# Обработка списка из строк файла

	if marker_layer_number in line:											# Определения текущего слоя
		position = line.find(marker_layer_number) + len(marker_layer_number)
		layer_number = int(line[position:line.find(")",position)])
		layer_number_line = index											# Текущий номер слоя
		flag_bridge_layer = False											# Сброс флага

	if (marker_bridge in line) and not flag_bridge_layer:
		lines[layer_number_line] += "M106 S" + str(bridge_fan_speed) + " ; Bridge Fan Advance\n"
		flag_bridge_layer = True
		print("layer " + str(layer_number) + " - line " + str(layer_number_line))

	if (marker_fan in line) and flag_bridge_layer:							# Смена скорости вентилятора внутри слоя
		if not (marker_stop in lines[index+1]) and not (marker_layer_change in lines[index+1]):	# Исключение смены скорости вентилятора в конце слоя
			lines[index] = marker_fan + str(bridge_fan_speed) + " ; Bridge Fan Advance\n"

	index += 1															# Счёт номера строки

gcode = ''.join(lines)													# Объединение строк после обработки

with open (file_output, 'w') as file:									# Открываем файл c g-кодом для записи
	file.write(gcode)														# Записываем результат обработки в файл

