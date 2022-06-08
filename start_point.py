#!/usr/bin/env python3

move_old = "G0 X20 Y20 Z0 F1200 ; MOVE TO START POSITION"				# Шаблон поиска строки перемещения в начальную точку
																		# Такая же строчка должна быть в стартовом коде PrusaSlicer

import sys
import os
import platform # библиотека для получения типа операционной системы

if len(sys.argv) > 1:													# Для отладки
	file_input = str(sys.argv[1])										# Получение пути к файлу с g-кодом
	file_output = file_input											# Для отладки
	
else:																	# Для отладки и запуска сценария из терминала (без PrusaSlicer) 
	file_input = "/tmp/.20150.gcode"
	file_output = file_input + ".new"

with open(file_input) as f:												# Открытие файла
	for line in f:														# Построчная обработка файла
		if ("move to first skirt point" or "move to first brim point") in line:	# Поиск по шаблону
			start_point_x = line.split(' ')[1]							# Разбиваем строку. Разделитель " ". Первый элемент X...
			start_point_x = start_point_x[1:]							# Получение координаты X
			
			start_point_y = line.split(' ')[2]							# Разбиваем строку. Разделитель " ". Второй элемент Y...
			start_point_y = start_point_y[1:]							# Получение координаты Y

			speed_fast = line.split(' ')[3]								# Разбиваем строку. Разделитель " ". Третий элемент F...
			speed_fast = speed_fast[1:]									# Получение скорости F
			
			# Новая строка
			move_new = "G1 X" + str(start_point_x) + " Y" + str(start_point_y) + " F" + str(speed_fast) + " ; MOVE TO START POSITION POST-PROCESSING"
			break														# Если совпадение найдено, завершить обработку строк файла

print ("file_input = " + file_input)									# Вывод данных в терминал
print ("start_point_x = " + str(start_point_x))
print ("start_point_y = " + str(start_point_y))
print ("speed_fast = " + str(speed_fast))
print (move_new)

with open (file_input, 'r') as f:										# Открываем файл для чтения
	old_data = f.read()													# Считываем содержимое файла в память

new_data = old_data.replace(move_old, move_new)							# Заменяем строку

with open (file_output, 'w') as f:										# Открываем файл для записи
	f.write(new_data)													# Записываем результат в файл
	f.write(new_data)

# Вывод уведомления через notify-send в Linux
#command = f'''
#notify-send {123} {file_output}
#'''
#os.system(command)
