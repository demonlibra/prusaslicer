#!/usr/bin/env python3

# ----------------------------- Параметры ------------------------------

marker = "MOVE TO START POSITION"										# Шаблон поиска строки перемещения в начальную точку
																		# Такой же маркер должен быть в стартовом коде PrusaSlicer
																		# Общий синтаксис строки должен быть следующим:
																		# G0 X20 Y20 Z0 F1200 ; MOVE TO START POSITION
# ======================================================================

import sys																# Иморт модуля sys
																		# sys.argv - список аргументов командной строки, которые причастны к сценарию
																		# sys.argv[0] - путь к файлу сценария
																		# sys.argv[1] - путь к файлу с g-кодом
																		
if len(sys.argv) > 1:													# Проверка получения более одного аргумента
	file_input = str(sys.argv[1])										# Получение пути к файлу с g-кодом
	file_output = file_input											# При запуске из PrusaSlicer записывать данные в тот же файл
	
else:																	# При запуске сценария из терминала (только для отладки) 
	file_input = "/home/demonlibra/test.gcode"							# Путь к тестовому файлу (только для отладки)
	file_output = file_input + ".new"									# Путь к файлу для сохранения результата (только для отладки)

with open(file_input) as file:											# Открытие файла с g-кодом

	for line in file:													# Построчная обработка файла

		if marker in line:												# Если строка содержит маркер
			move_old = line												# Сохраняем старую строку для последующей замены

			speed = line[line.find("F"):line.find(";")]					# Получаем часть строки от символа F до точки с запятой
			speed = speed.split(' ')[0]									# Разбиваем строку. Разделитель " ". Первый элемент - скорость F.

			start_point_z = line[line.find("Z"):line.find(";")]			# Получаем часть строки от символа Z до точки с запятой
			start_point_z = start_point_z.split(' ')[0]					# Разбиваем строку. Разделитель " ". Первый элемент - координата Z.

		if ("move to first skirt point" or "move to first brim point") in line:	# Поиск первой строки юбки или каймы
			start_point_x = line[line.find("X"):line.find(";")]			# Получаем часть строки от символа X до точки с запятой
			start_point_x = start_point_x.split(' ')[0]					# Разбиваем строку. Разделитель " ". Первый элемент - координата X.
			
			start_point_y = line[line.find("Y"):line.find(";")]			# Получаем часть строки от символа Y до точки с запятой
			start_point_y = start_point_y.split(' ')[0]					# Разбиваем строку. Разделитель " ". Первый элемент - координата Y.

			break														# Если первая команда юбки или каймы найдена, завершить обработку строк файла


# Новая строка перемещения в начальные координаты печати
move_new = "G1 " + str(start_point_x) + " " + str(start_point_y) + " " + str(start_point_z) + " " + str(speed) + " ; MOVE TO START POSITION POST-PROCESS\n"

print ("file_input = " + file_input)									# Вывод данных в терминал для отладки
print ("file_output = " + file_output)
print ("start_point_x = " + str(start_point_x))
print ("start_point_y = " + str(start_point_y))
print ("start_point_z = " + str(start_point_z))
print ("speed = " + str(speed))
print ("move_old = " + move_old)
print ("move_new = " + move_new)

with open (file_input, 'r') as file:									# Открываем оригинальный файл c g-кодом для чтения
	old_data = file.read()												# Считываем содержимое файла в память

new_data = old_data.replace(move_old, move_new)							# Заменяем строку перемещения в начальные координаты печати

with open (file_output, 'w') as file:									# Открываем файл c g-кодом для записи
	file.write(new_data)												# Записываем результат в файл
