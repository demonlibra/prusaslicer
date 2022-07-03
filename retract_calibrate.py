#!/usr/bin/env python3

# ------------------------------ Описание ------------------------------

'''

Сценарий добавляет строки изменения ретракта прошивки через заданный шаг.

Подробности в теме "Постобработка G-кода в PrusaSlicer" форума UNI:
https://uni3d.store/viewtopic.php?t=1041

Разместите две цилиндра на краях стола.
Количество периметров: 1
Количество слоёв крышки и дна: 0

Добавьте в список скриптов постобработки путь к сценарию с аргументами.
Например:
/home/demonlibra/.config/PrusaSlicer/post_process/retract_calibrate.py --lerdge --start=0.5 --step=0.2 --step_height=3 --speed=25 --z_hope=0;

Аргументы сценария:
--start=...			Начальное значение длины ретракта, мм (по умолчанию 0).
--step=...			Шаг изменения длины ретракта, мм (по умолчанию 0.2)
--step_height=...	Высота печати с одной длиной ретракта, мм (по умолчанию 5)
--speed=...			Скорость ретракта, мм/сек (по умолчанию 20)
--z_hope=...		Подъём головы при ретракте, мм (по умолчанию 0)
--lerdge			Указать для платы Lerdge (добавляет команду M208)

'''

# -------------------------- Импорт библиотек --------------------------

import argparse															# Импорт модуля обработки аргументов командной строки


# ------------- Получение аргументов переданных сценарию ---------------

parser = argparse.ArgumentParser()

parser.add_argument('--start', default='0', help='Начальное значение длины ретракта, мм')
parser.add_argument('--step', default='0.2', help='Шаг изменения длины ретракта, мм')
parser.add_argument('--step_height', default='5', help='Высота печати с одной длиной ретракта, мм')
parser.add_argument('--speed', default='20', help='Скорость ретракта, мм/сек')
parser.add_argument('--z_hope', default='0', help='Подъём головы при ретракте, мм')
parser.add_argument('--lerdge', action='store_true', help='Указать для прошивки Lerdge')
parser.add_argument('file', help="Путь к g-коду", nargs="+")
args = parser.parse_args()

file_input=args.file[0]													# Извлечение аргумента, путь к временному g-коду
if len(args.file) > 1:													# Если аргументов 2,
	file_output=args.file[1]												# использовать 2-й для отладки
else:
	file_output=file_input													# иначе записывать результат в исходный файл

print("file_input = " + file_input)
print("file_output = " + file_output)
print("step_height = " + str(args.step_height))
print("start = " + str(args.start))
print("step = " + str(args.step))
print("Lerdge = " + str(args.lerdge))

# ------------------- Извлечение данных из g-кода ----------------------

marker_z=";Z:"															# Метка текущей высоты Z

with open(file_input) as file:

	for line in file:													# Перебор строк файла
		
		if marker_z in line:											# Поиск максимальной высоты печати
			model_height = line[len(marker_z):]
			model_height = float(model_height)

print("Высота_печати = " + str(model_height))


# -------------------------- Изменение кода ----------------------------

with open(file_input) as file:											# Открываем файл для чтения
	lines = file.readlines()												# Заносим все строки файла в список

index_line = 0															# Счётчик строк
index_step = 1															# Счётчик шагов

for line in lines:														# Обработка списка из строк файла

	if marker_z in line:												# Если строка содержит маркер высоты

		height = float(line[len(marker_z):])							# Текущая высота

		if height == float(index_step * float(args.step_height)):		# Если достигнут очередной шаг высоты
			if args.lerdge:												# Для прошивки Lerdge
				new_line = "M207 S" + str(round(float(args.start)+index_step*float(args.step),2)) + " F" + str(int(args.speed)*60) + " Z" + args.z_hope + " ; Параметр ретракта\n"
				new_line += "M208 S" + str(round(float(args.start)+index_step*float(args.step),2)) + " F" + str(int(args.speed)*60) + " Z" + args.z_hope + " ; Параметр возврата\n"
			else:														# Для других прошивок
				new_line = "M207 S" + str(round(float(args.start)+index_step*float(args.step),2)) + " F" + str(int(args.speed)*60) + " Z" + args.z_hope + " ; Параметр ретракта\n"
				
			print(line + new_line)
			lines[index_line] = line + new_line							# Замена строки
			index_step += 1												# Увеличение счётчика шагов

	index_line += 1														# Увеличение счётчика строк

# ------------------- Вставка начальных параметров ---------------------

if args.lerdge:
	new_line = "; ----- Калибровка ретракта -----\n"
	new_line += "M207 S" + str(args.start) + " F" + str(int(args.speed)*60) + " Z" + args.z_hope + " ; Установка начальных параметров ретракта\n"
	new_line += "M208 S" + str(args.start) + " F" + str(int(args.speed)*60) + " Z" + args.z_hope + " ; Установка начальных параметров возврата\n\n"
else:
	new_line = "; ----- Калибровка ретракта -----\n"
	new_line += "M207 S" + str(args.start) + " F" + str(int(args.speed)*60) + " Z" + args.z_hope + " ; Установка начальных параметров ретракта\n;\n"

lines[0] = new_line + lines[0]

gcode = ''.join(lines)													# Объединение строк после обработки

with open (file_output, 'w') as file:									# Открываем файл c g-кодом для записи
	file.write(gcode)														# Записываем результат обработки в файл

