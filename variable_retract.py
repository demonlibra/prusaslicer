#!/usr/bin/python3

# ------------------------------ Описание ------------------------------

'''

Сценарий добавляет команды задания длины ретракта из прошивки
в зависимости от длины перемещения.

Подробности в теме "Постобработка G-кода в PrusaSlicer" форума UNI:
https://uni3d.store/viewtopic.php?t=1041

Включите функцию "Ретракт из прошивки"
	Настройки принтера -> Общие -> Дополнительно -> Использовать ретракт из прошивки

Добавьте в список скриптов постобработки пути к интепритатору и сценарию с аргументами.
Например:
/usr/bin/python3 /home/demonlibra/.config/PrusaSlicer/post_process/variable_retract.py --firmware=klipper --min_retract=0.3 --min_move=3 --max_retract=2 --max_move=200 --speed=25 --z_hope=0;

Аргументы сценария:
	--min_retract=...		Минимальная длина ретракта, мм (по умолчанию 0.5).
	--min_move=...			До какого перемещения задавать минимальный ретракт, мм (по умолчанию 5)
	
	--max_retract=...		Максимальная длина ретракта, мм (по умолчанию 1.5)
	--max_move=...			От какого перемещения задавать максимальный ретракт, мм (по умолчанию 200)

	--firmware=...			Тип прошивки (по умолчанию Marlin, добавляет команду M207)
	--firmware=lerdge		Указать для прошивки Lerdge (добавляет команды M207 и M208)
	--firmware=klipper	Указать для прошивки Klipper (добавляет команду SET_RETRACTION)

'''

# -------------------------- Импорт библиотек --------------------------

import argparse	# Импорт модуля обработки аргументов командной строки

# ------------- Получение аргументов переданных сценарию ---------------

parser = argparse.ArgumentParser()

parser.add_argument('--min_retract', default='0.5', help='Минимальная длина ретракта, мм')
parser.add_argument('--min_move', default='5', help='До какого перемещения задавать минимальный ретракт, мм')
parser.add_argument('--max_retract', default='1.5', help='Максимальная длина ретракта, мм')
parser.add_argument('--max_move', default='200', help='От какого перемещения задавать максимальный ретракт, мм')
parser.add_argument('--firmware', default='marlin', help='Указать тип прошивки: klipper, lerdge, marlin, rrf')
parser.add_argument('file', help="Путь к g-коду", nargs="+")
args = parser.parse_args()

file_input=args.file[0]																	# Извлечение аргумента, путь к временному g-коду
if len(args.file) > 1:																	# Если аргументов 2,
	file_output=args.file[1]																# использовать 2-й аргумент для отладки
else:																							# иначе
	file_output=file_input																	# записывать результат в исходный файл

print("file_input = " + file_input)
print("file_output = " + file_output)

with open(file_input) as file:														# Открываем файл для чтения
	lines = file.readlines()															# Заносим все строки файла в список

index_line = 0																				# Счётчик строк

for line in lines:																		# Обработка списка из строк файла

	if "G10 ; retract" in line:														# Если строка содержит команду ретракта
		i = 0
		while True:																			# Поиск последней команды перемещения 
			i += 1
			move = lines[index_line-i]
			if ('G1' in move or 'G0' in move) and 'X' in move and 'Y' in move:
				#print(move)
				x1 = move[move.find("X")+1:]
				x1 = x1.split(' ')[0]
				x1 = float(x1)
				y1 = move[move.find("Y")+1:]
				y1 = y1.split(' ')[0]
				y1 = float(y1)
				
				break

		while True:																			# Поиск следующей команды перемещения 
			i += 1
			move = lines[index_line+i]
			if ('G1' in move or 'G0' in move) and 'X' in move and 'Y' in move:
				#print(move)
				x2 = move[move.find("X")+1:]
				x2 = x2.split(' ')[0]
				x2 = float(x2)
				y2 = move[move.find("Y")+1:]
				y2 = y2.split(' ')[0]
				y2 = float(y2)
				
				break

		print(index_line)
		print('x1='+str(x1) + ' y1='+str(y1) + ' x2='+str(x2) + ' y2='+str(y2))

		move_length = ((x1-x2)**2 + (y1-y2)**2)**0.5								# Длина перемещения
		move_length = round(move_length,1)
		
		print('move_length=' + str(move_length))
	
		if move_length > float(args.max_move):
			retract_length = float(args.max_retract)
		elif move_length < float(args.min_move):
			retract_length = float(args.min_retract)
		else:
			# (y - y1) / (y2 - y1) = (x - x1) / (x2 - x1)						# Уравнение прямой
			retract_length = (float(args.max_retract)-float(args.min_retract)) * (move_length-float(args.min_move)) / (float(args.max_move)-float(args.min_move)) + float(args.min_retract)
			retract_length = round(retract_length, 1)

		print('retract_length=' + str(retract_length))
			
		if args.firmware.casefold() == 'klipper':								# Формирование кода для прошивки Klipper
			new_line = "SET_RETRACTION RETRACT_LENGTH={retract_extra+" + str(retract_length) + "} ; Ретракт " + str(retract_length) + " мм для перемещения " + str(move_length) + " мм\n"

		elif args.firmware.casefold() == 'lerdge':									# Формирование кода для прошивки Lerdge
			new_line = "M207 S" + str(retract_length) + " ; Ретракт " + str(retract_length) + " мм для перемещения " + str(move_length) + " мм\n"
			new_line += "M208 S" + str(retract_length) + " ; Параметр возврата\n"

		elif args.firmware.casefold() == 'rrf':									# Формирование кода для прошивки Lerdge
			new_line = "M207 S{var.retract_extra+" + str(retract_length) + "} ; Ретракт " + str(retract_length) + " мм для перемещения " + str(move_length) + " мм\n"
			
		else:																					# Формирование кода для других прошивок
			new_line = "M207 S" + str(retract_length) + " ; Ретракт " + str(retract_length) + " мм для перемещения " + str(move_length) + " мм\n"

		print(new_line)
		lines[index_line] = new_line + line											# Замена строки

	index_line += 1																		# Увеличение счётчика строк

# ------------------- Вставка начальных параметров ---------------------

if args.firmware.casefold() == 'rrf':
	new_line = "var retract_extra=0 ; Переменная для изменения ретракта во время печати\n;\n"

elif args.firmware.casefold() == 'klipper':
	new_line = "{% set retract_extra=0 %} ; Переменная для изменения ретракта во время печати\n;\n"

lines[0] = new_line + lines[0]

# ---------------------- Сохранение результата -------------------------

gcode = ''.join(lines)																	# Объединение строк после обработки

with open (file_output, 'w') as file:												# Открываем файл c g-кодом для записи
	file.write(gcode)																		# Записываем результат обработки в файл

