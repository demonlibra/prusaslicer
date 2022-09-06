#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------ Описание ------------------------------

''' Сценарий заменяет строки ретракта из слайсера (G1 E...) на ретракт из прошивки (G10/G11).
В качестве аргументов необходимо обязательно передать путь к каталогу с файлами gcode.

Например

	python3 g1_2_g10.py 'Нарезки'

Дополнительные аргументы

	--sufix='_g10'   -   Суфикс нового имени файла


python3 g1_2_g10.py --sufix='retract_g10' 'Нарезки'
'''


# -------------------------- Импорт библиотек --------------------------

import os
import argparse


# ---------------------------- Аргуметны -------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('--sufix', default='_g10', help='Суфикс нового имени файла')
parser.add_argument('path', help="Путь к g-коду", nargs="+")
args = parser.parse_args()


# ---------------------- Функция обработки файла -----------------------

def retract(file_input, file_output):

	with open(file_input) as file:										# Открываем файл для чтения
		lines = file.readlines()										# Заносим все строки файла в список

	index = 0
	extrude_now = 0
	extrude_before = 0
	flag_start = False
	flag = False

	for line in lines:													# Построчная обработка файла

		if 'Ending Start' in line:
			flag_start = True

		if flag_start and ('G1 ' in line) and ('E' in line.split(';')[0]) and (line[0] != ';'):

			if not flag:
				extrude_before = extrude_now

			extrude_now = line[line.find('E')+1:]
			extrude_now = float(extrude_now.split(' ')[0])

			if extrude_now < extrude_before:
				#print (str(index+1) + ':G10  ' + str(extrude_now))
				lines[index] = 'G10\n'
				flag = True
			elif (extrude_now == extrude_before) and flag:
				#print (str(index+1) + ':G11  ' + str(extrude_now))
				lines[index] = 'G11\n'
				flag = False

		index += 1

	gcode = ''.join(lines)

	with open (file_output, 'w') as file:								# Открываем файл c g-кодом для записи
		file.write(gcode)												# Записываем результат обработки в файл


# --------------------- Перебор файлов в каталоге ----------------------

for dirpath, dirnames, filenames in os.walk(str(args.path[0])):
	for filename in filenames:
		if filename.split('.')[-1].casefold() == 'gcode':				# Только если расширение файла gcode (без учёта регистра)
			path = os.path.join(dirpath, filename)						# Путь к файлу
			print(path)
			file_input = path
			file_output = path + args.sufix

			retract(file_input, file_output)							# Запуск функции
