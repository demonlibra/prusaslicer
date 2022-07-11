#!/usr/bin/python3

# ----------------------------- Описание -------------------------------

'''

Сценарий включает функцию "UNI SUPER LA" (только для плат UNI) перед печатью периметров.

Подробности в теме "Постобработка G-кода в PrusaSlicer" форума UNI:
https://uni3d.store/viewtopic.php?t=1041

Параметры S и U можно указать в любом из доступных полей слайсера,
например "Заметки" или "Пользовательский G-код" профиля прутка.
Ключевой синтаксис находится до знака точки с запятой и по умолчанию следующий:
UNI_SUPER_LA_S=0.105 ; Параметр S для функции SUPER LA
UNI_SUPER_LA_U=0.025 ; Параметр U для функции SUPER LA

При необходимости изменить синтаксис метки добавьте аргументы --markerS и --markerU

Для отладки выполнить в терминале:
python3 uni_super_la.py <"исходный_файл_с_g-кодом"> <"файл_для_сохранения_результата">

'''

# -------------------------- Импорт библиотек --------------------------

import sys																# Импорт библиотеки sys
import argparse															# Импорт модуля обработки аргументов командной строки

# ---------------------------- Аргуметны -------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('--markerS', default='UNI_SUPER_LA_S=', help='Маркер параметра S')
parser.add_argument('--markerU', default='UNI_SUPER_LA_U=', help='Маркер параметра U')
#parser.add_argument('--test', action='store_true', help='Калибровка параметра')
parser.add_argument('file', help="Путь к g-коду", nargs="+")
args = parser.parse_args()

file_input=args.file[0]													# Извлечение аргумента, путь к временному g-коду
if len(args.file) > 1:													# Если аргументов 2,
	file_output=args.file[1]												# использовать 2-й аргумент для отладки
else:
	file_output=file_input													# иначе записывать результат в исходный файл

# -------------------- Извлечение параметров S и U ---------------------

marker_s = args.markerS
marker_u = args.markerU
marker_type = ";TYPE:"													# Маркер для поиска типа линий

super_la_s = ""
super_la_u = ""

with open(file_input) as file:											# Открытие файла с g-кодом
	for line in file:														# Построчная обработка файла

		if marker_type in line:												# Если хотя бы в одной строке присутствует маркер типа линий
			flag_verbose = True													# установить флаг
			
		if marker_s in line:													# Если строка содержит маркер параметра S
			position_s = line.find(marker_s) + len(marker_s)					# Позиция параметра S в строке
			super_la_s = line[position_s:line.find(" ",position_s)]					# Получаем значение параметра S

		if marker_u in line:													# Если строка содержит маркер параметра U
			position_u = line.find(marker_u) + len(marker_u)					# Позиция параметра S в строке
			super_la_u = line[position_u:line.find(" ",position_u)]					# Получаем значение параметра S

		if super_la_s and super_la_u:											# Если параметры S и U найдены,
			break																	# завершить обработку строк файла

# --------------- Проверка полученных параметров S и U -----------------

try:
	print(float(super_la_s))											# Попытаться преобразовать super_la_s в число и показать результат
except:																	# При ошибке завершаем сценарий и выводим сообщение
	sys.exit("\n!!! Внимание !!!\nНе найдено значение S функции UNI SUPER LA.\nПроверьте синтаксис и введёные значения в профиле PrusaSlicer.")

try:
	print(float(super_la_u))											# Попытаться преобразовать super_la_u в число и показать результат
except:																	# При ошибке завершаем сценарий и выводим сообщение
	sys.exit("\n!!! Внимание !!!\nНе найдено значение U функции UNI SUPER LA.\nПроверьте синтаксис и введёные значения в профиле PrusaSlicer.")


# -------------------------- Изменение кода ----------------------------

set_super_la = "M900 S" + super_la_s + " U" + super_la_u + " ; Set parameters UNI SUPER LA"	# Формирование строки включения UNI SUPER LA
reset_super_la = "M900 S0 U0 ; Reset parameters UNI SUPER LA"								# Формирование строки выключения UNI SUPER LA

with open(file_input) as file:											# Открываем файл для чтения
	lines = file.readlines()												# Заносим все строки файла в список

index = 0																# Счётчик строк
flag = False															# Флаг состояния UNI SUPER LA

for line in lines:														# Обработка списка из строк файла

	if marker_type in line:													# Если строка содержит указание типа линии,
		if "Perimeter" in line or "External perimeter" in line:					# и если это начало периметра,
			if not flag:															# и если UNI SUPER LA не включался ранее 
				lines[index] = line + set_super_la + "\n"								# Включить UNI SUPER LA
				flag = True																# Установить флаг

		elif flag == True:														# Если это НЕ начало периметра и ранее был включен UNI SUPER LA
			lines[index] = line + reset_super_la + "\n"								# Выключить UNI SUPER LA
			flag = False															# Сбросить флаг

	index += 1																# Счёт номера строки

lines[0] = ";UNI SUPER LA postprocessing\nM900 S0 U0 ; Reset UNI SUPER LA\n;\n" + lines[0]	# Сброс UNI SUPER LA в начале
gcode = ''.join(lines)													# Объединение строк после обработки

with open (file_output, 'w') as file:									# Открываем файл c g-кодом для записи
	file.write(gcode)														# Записываем результат обработки в файл

# ======================================================================

# ------------------------------ Отладка -------------------------------

debug_text = "file_input = " + file_input + "\n"						# Формирование строки с данными отладки
debug_text += "super_la_s = " + str(super_la_s) + "\n"
debug_text += "super_la_u = " + str(super_la_u) + "\n"
debug_text += set_super_la + "\n"
debug_text += reset_super_la + "\n"

print (debug_text)														# Вывод информации отладки в терминал

# ======================================================================
