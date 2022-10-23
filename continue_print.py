#!/usr/bin/python3

# ------------------------------ Описание ------------------------------

'''

Сценарий комментирует часть кода для продолжения печати с определённого слоя или высоты.

Подробности в теме "Постобработка G-кода в PrusaSlicer" форума UNI:
https://uni3d.store/viewtopic.php?t=1041

Для работы сценария в исходной нарезки должны быть включены следующие функции:
   - "Использовать относительные координаты для экструдера"
     Настройки принтера -> Общие -> Дополнительно -> Использовать относительные координаты для экструдера

Добавьте в список скриптов постобработки пути к интепритатору и сценарию с аргументами.
Например:
/usr/bin/python3 /home/demonlibra/.config/PrusaSlicer/post/continue_print.py --from_layer=43;
/usr/bin/python3 /home/demonlibra/.config/PrusaSlicer/post/continue_print.py --from_height=15.1;

Аргументы сценария:
	--from_layer=...		Продолжить с номера слоя
	--from_height=...		Продолжить с высоты, мм

'''

# -------------------------- Импорт библиотек --------------------------

import argparse			# Импорт модуля обработки аргументов командной строки
import sys
from os import getenv	# Импорт модуля для получения значений переменных окружения
import re					# Импорт модуля регулярных выражений

# ------------- Получение аргументов переданных сценарию ---------------

parser = argparse.ArgumentParser()

parser.add_argument('--from_layer', default=None, help='Продолжить с номера слоя')
parser.add_argument('--from_height', default=None, help='Продолжить с высоты, мм')
parser.add_argument('file', help="Путь к g-коду", nargs="+")
args = parser.parse_args()

# ------- Использовать относительные координаты для экструдера ---------

try:
	use_relative_e_distances = int(getenv('USE_RELATIVE_E_DISTANCES'))	# Включены ли относительные координаты экструдера
	if not use_relative_e_distances:
		sys.exit("\n!!! Внимание !!!\Для работы сценария до нарезки исходной модели должна быть включена функция:\nНастройки принтера -> Общие -> Дополнительно -> Использовать относительные координаты для экструдера")
except Exception:
	print('Не удалось считать параметр use_relative_e_distances из PrusaSlicer')
	
try:
	layer_height = float(getenv('LAYER_HEIGHT'))									# Считывание высоты слоя из PrusaSlicer
except Exception:
	layer_height = 0.2
	print('Не удалось считать параметр layer_height из PrusaSlicer')

# ------------------------ Проверка аргументов -------------------------

print('\nfrom_height = ' + str(args.from_height))
print('from_layer = ' + str(args.from_layer))

if args.from_layer and args.from_height:
	sys.exit("\n!!! Внимание !!!\Нельзя одновременно использовать аргументы --from_height и --from_layer")

if not args.from_layer and not args.from_height:
	sys.exit("\n!!! Внимание !!!\Необходимо указать высоту при помощи аргумента --from_height или номер слоя --from_layer")
	
file_input=args.file[0]																	# Извлечение аргумента, путь к временному g-коду
if len(args.file) > 1:																	# Если аргументов 2,
	file_output=args.file[1]																# использовать 2-й аргумент для отладки
else:																							# иначе
	file_output=file_input																	# записывать результат в исходный файл

print('\nfile_input = ' + file_input)
print('file_output = ' + file_output + '\n')

# ---------------------------- Обработка -------------------------------

with open(file_input) as file:														# Открываем файл для чтения
	lines = file.readlines()															# Заносим все строки файла в список

i = 0																							# Счётчик строк
flag_comment = False																		# Флаг начала комментирования строк
flag_start = True																			# Флаг стартового кода

for i in range(0,len(lines)):															# Обработка списка из строк файла

	if args.from_layer \
	and re.search(r'move to next layer \((\d*)\)', lines[i]):				# Если указан номер слоя и строка содержит маркер смены слоя				
		flag_start = False																# Это уже не стартовый код
		line = lines[i]
		try:
			layer_num = int(line[line.find('(')+1:line.find(')')])			# Текущий номер слоя
		except Exception:
			sys.exit('\n!!! Внимание !!!\Не удалось определить номер слоя в строке ' + str(i+1))
		if layer_num < int(args.from_layer):
			print(str(i) + ' layer ' + str(layer_num))
			flag_comment = True
		else:
			flag_comment = False
			break
	
	if args.from_height \
	and lines[i].startswith(';Z:'):													# Если указана высота слоя и строка содержит маркер смены слоя
		flag_start = False																# Это уже не стартовый код
		line = lines[i]
		try:
			height = float(line[line.find(':')+1:])								# Текущая высота модели
		except Exception:
			sys.exit('\n!!! Внимание !!!\Не удалось определить высоту в строке ' + str(i+1))
		if height < float(args.from_height):
			print(str(i) + ' height ' + str(height))
			flag_comment = True
		else:
			flag_comment = False
			break

	if flag_comment:
		if lines[i][0] != ';':
			lines[i] = ';' + lines[i]

	if flag_start and re.search(r'^(G0|G1)(.*)Z', lines[i]):					# Поиск и комментирование строк перемещений Z в стартовом коде
		line = lines[i]
		try:
			height = float(line[line.find('Z')+1:].split(' ')[0])
			print(str(i+1) + ' Z' + str(height))
		except Exception:
			sys.exit('\n!!! Внимание !!!\Не удалось определить высоту в строке ' + str(i+1))
		if args.from_height and (height < float(args.from_height)):
			lines[i] = ';' + lines[i]
		if args.from_layer and (height < (layer_height*float(args.from_layer))):
			lines[i] = ';' + lines[i]

	i += 1																					# Увеличение счётчика строк

lines[i] += 'G0 E50 F300\n'															# Выдавить 50 мм филамента
lines[i] += 'G10\n'																		# Ретракт

for j in range(i,len(lines)):
	if re.search(r'^(G0|G1)(.*)E', lines[j]):
		lines[j] = 'G11\n' + lines[j]
		break
	
# ---------------------- Сохранение результата -------------------------

gcode = ''.join(lines)																	# Объединение строк после обработки

with open (file_output, 'w') as file:												# Открываем файл c g-кодом для записи
	file.write(gcode)																		# Записываем результат обработки в файл

