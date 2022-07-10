#!/usr/bin/python3

# ----------------------------- Описание -------------------------------

'''

Сценарий изменяет скорость печати внешних периметров с нависанием.
Угол нависания определяется поддержками.
Поддержки удаляются из кода автоматически.

Подробности в теме "Постобработка G-кода в PrusaSlicer" форума UNI:
https://uni3d.store/viewtopic.php?t=1041

В профилях PrusaSlicer необходимо:
- Включить функцию "Подробный G-код"
- Включить функции "Генерация вспомогательных структур" и "Автоматически созданные поддержки".
- Задать "Угол нависания поддержки" для определения нависающих периметров.
- Включить функцию "Синхронизация со слоями поддержки".
- Включить функцию "Использовать относительные координаты для экструдера (E)".
- Включить функцию "Использовать ретракт из прошивки".


Аргументы сценария:
   --speed=...   Скорость нависающих периметров
                 Если задать < 1.0, то уменьшать скорость пропорционально
                 Если задать > 1, то считать скорость постоянной
                 --speed=20 - задать скорость периметра 20 мм/сек

Для отладки выполнить в терминале:
python3 overhang_perimeters.py <"исходный_файл_с_g-кодом"> <"файл_для_сохранения_результата">

'''

# -------------------------- Импорт библиотек --------------------------

import sys																# Импорт библиотеки sys
import argparse															# Импорт модуля обработки аргументов командной строки

# ---------------------------- Аргуметны -------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('--speed', default="20", help='Скорость')			# Задание скорости
parser.add_argument('file', help="Путь к g-коду", nargs="+")			# Задание путей к файлам с g-кодом
args = parser.parse_args()

file_input=args.file[0]													# Извлечение аргумента, путь к временному g-коду
if len(args.file) > 1:													# Если аргументов 2,
	file_output=args.file[1]											 # использовать 2-й аргумент для отладки
else:
	file_output=file_input												 # иначе записывать результат в исходный файл

# ------------------- Маркер для поиска типа линий ---------------------

marker_type = ";TYPE:"
marker_support_start = "move to first support material"
marker_support_interface = ";TYPE:Support material interface"
marker_perimeter = ";TYPE:Perimeter"
marker_ext_perimeter = ";TYPE:External perimeter"
marker_layer = "move to next layer ("
marker_speed = "G1 F"

# -------------------------- Изменение кода ----------------------------

if int(float(args.speed)) > 1:											# Если задана скорость > 1
	speed = int(float(args.speed))*60										# скорость в мм/мек
	change_speed = "G1 F" + str(speed) + " ; overhang_perimeters\n"		# Формирование строки изменения скорости
	print("A"+str(change_speed))

with open(file_input) as file:											# Открываем файл для чтения
	lines = file.readlines()												# Заносим все строки файла в список

index = 0																# Счётчик строк
list_layers_overhang = []
layer_number = 0
flag_perimeter = False
flag_erase = False
												
for line in lines:														# Обработка списка из строк файла

	if marker_layer in line:											# Определения текущего слоя
		position = line.find(marker_layer) + len(marker_layer)			
		layer_number = int(line[position:line.find(")",position)])

	if (marker_support_interface in line) and ((layer_number+1) not in list_layers_overhang):
		list_layers_overhang.append(layer_number+1)						# Формирование списка слоёв с нависающими периметрами

	if (marker_ext_perimeter in line): # or (marker_perimeter in line):
		flag_perimeter = True											# Следующий блок является периметром
	elif marker_type in line:
		flag_perimeter = False											# Следующий блок НЕ является периметром

	if (layer_number in list_layers_overhang) and (marker_speed in line) and flag_perimeter:
		if int(float(args.speed)) < 1:
			old_speed = int(line[len(marker_speed):-1])
			new_speed = old_speed * float(args.speed)
			change_speed = "G1 F" + str(new_speed) + " ; overhang_perimeters\n"	# Формирование строки изменения скорости

		lines[index] = change_speed										# Замена строки задания скорости
	
	if marker_support_start in line:									# Установка флага блока заполнения
		flag_erase = True
	elif "move to first" in line:
		flag_erase = False												# Сброс флага блока заполнения

	if flag_erase:														# Если блок относится к заполнению,
		lines[index] = ""												 # стереть строку

	index += 1															# Счёт номера строки

print (list_layers_overhang)
gcode = ''.join(lines)													# Объединение строк после обработки

with open (file_output, 'w') as file:									# Открываем файл c g-кодом для записи
	file.write(gcode)														# Записываем результат обработки в файл

