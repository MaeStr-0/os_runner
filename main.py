import math
import re
from getpass import getpass

#МЕТОДИЧКА ПО FAT https://drive.google.com/file/d/19GbO9TWT19yNlAx5nR7CA8Oi0FNyufrg/view
#МЕТОДИЧКА ПО NTFC https://drive.google.com/file/d/1zPc29KquTsB0yoKcUOodIT4ZtslTv-Xy/view
#САЙТ С ФАЙЛОВЫМИ СИСТЕМАМИ https://fat.bk252.ru/

#ШАГ №1
file_name = input("Введи путь до файла формата xxx/xxx/xxx\n")
file_name = file_name.split(sep='/')
file_name = list(filter(None, file_name))
download_sector = input("\nВставь начальную таблицу\n")
print("\n")
lines = []

while True:
    download_sector = input()
    # 👇️ Если пользователь нажал Enter без ввода значения, прервать цикл
    if download_sector == '':
        break
    else:
        lines.append(download_sector + '\n')

lines_str = str(lines)
results = re.search(r'FAT', lines_str)
results1 = re.search(r'FAT12', lines_str)

zones = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0}

if results is not None:
    if results1 is not None:
        zones['1'] = 'FAT12'
    else:
        zones['1'] = 'FAT16'
else:
    print("это не fat")

pos = [[43, 48], [52, 57], [12, 17], [27, 32], [1, 1]]
numbers = ['2', '4', '6', '7']
rows = [0, 0, 1, 1]
i = 0
for row in rows:
    zone = lines[row]
    zone = zone[pos[i][0]:pos[i][1]].split()
    zone.reverse()
    zone = ''.join(zone)
    zone = int(zone, 16)
    zones[f'{numbers[i]}'] = zone
    i += 1

zone = lines[0]
zone = zone[49:51]
zone = int(zone, 16)
zones['3'] = zone
zone = lines[1]
zone = zone[9:11]
zone = int(zone, 16)
zones['5'] = zone

print('Система хранения                      | ', f'{zones['1']}')
print('Размер сектора                        | ', f'{zones['2']}', ' байт')
print('Количество секторов в кластере        | ', f'{zones['3']}', ' сектор')
print('Количество зарезервированных секторов | ', f'{zones['4']}', ' секторов')
print('Количество FAT-таблиц                 | ', f'{zones['5']}', ' штуки')
print('Размер корневой директории            | ', f'{zones['6']}', ' байт')
print('Размер одной FAT-таблицы              | ', f'{zones['7']}', ' секторов')
print('-----------------------------------------------------------------------')
pos_root = int(zones['4']) + (int(zones['5']) * int(zones['7']))
print('Сектор корневой папки                 | ', f'{pos_root}', 'сектор')
print('-----------------------------------------------------------------------')
root_table = input(f'\033[31mПЕРЕЙДИ В {pos_root}-Й СЕКТОР И ВСТАВЬ СЮДА ТАБЛИЦУ\033[0m\n')

#ШАГ №3, 4, 5

for z in range(0, len(file_name)):

    lines = []
    while True:
        root_table = input()
        if root_table == '':
            break
        else:
            lines.append(root_table + '\n')

    lines_str = str(lines)

    for i in range(0, 31):
        match = re.findall(f"{file_name[z]}", lines[i], re.IGNORECASE)
        # print(match)
        if not match:
            continue
        else:
            break

    # print(lines[4])
    #print(file_name[0])

    pos_start_data = int(pos_root) + 32
    pos_directory = [lines[i], lines[i + 1]]
    name_dir = file_name[z]
    type_dir = pos_directory[0][43:46]
    type_dir = int(type_dir)
    if type_dir == 10:
        number_dir = pos_directory[1][40:45]
        number_dir = number_dir.split()
        number_dir.reverse()
        number_dir = ''.join(number_dir)
        number_dir = int(number_dir, 16)
        size_dir = pos_directory[1][46:57]
        road_args = {'1': name_dir, '2': type_dir, '3': number_dir, '4': size_dir}
        next_claster = (number_dir - 2) * zones['3'] + pos_start_data

        print('-----------------------------------------------------------------------')
        print("Имя директории                        |", road_args['1'])
        print("Атрибут                               |", ('Папка' if road_args['2'] == 10 else 'Файл'))
        print("Номер первого кластера директории     |", road_args['3'])
        print("Размер директории                     |", road_args['4'])
        print('-----------------------------------------------------------------------')
        root_table = input(f'\033[31mПЕРЕЙДИ В {next_claster}-Й СЕКТОР И ВСТАВЬ СЮДА ТАБЛИЦУ\033[0m\n')

    else:
        size_dir = pos_directory[1][46:57]
        size_dir = size_dir.split()
        size_dir.reverse()
        size_dir = ''.join(size_dir)
        size_dir = int(size_dir, 16)
        print(size_dir)
        number_dir = pos_directory[1][40:45]
        number_dir = number_dir.split()
        number_dir.reverse()
        number_dir = ''.join(number_dir)
        number_dir = int(number_dir, 16)
        file_args = {'1': file_name[z], '2': 'Файл', '3': number_dir, '4': size_dir}
        size_of_clasters = int(zones['2']) * int(zones['3'])
        value_of_clasters = math.ceil(size_dir / size_of_clasters)
        print('-----------------------------------------------------------------------')
        print('Название файла                        |', file_args['1'])
        print('Размер файла                          |', size_dir, 'байт')
        print('Количество занимаемых кластеров       |', value_of_clasters)
        print('Первый кластер                        |', file_args['3'])
        print('-----------------------------------------------------------------------')
        file_clasters = input(f'\033[31mПЕРЕЙДИ В {zones['4']}-Й СЕКТОР И ВСТАВЬ СЮДА ТАБЛИЦУ\033[0m\n')

#ШАГ №6

lines = []
while True:
    file_clasters = input()
    if file_clasters == '':
        break
    else:
        lines.append(file_clasters + '\n')

lines_str = str(lines)

offset = lines[0][:9]
offset = int(offset, 16)

if zones['1'] == 'FAT12':
    if (offset + number_dir * 1.5)%10!=0:
        part = True
    else:
        part = False

    loc = math.floor(offset + number_dir * 1.5)
    loc = hex(loc)

    coord = {'0':9,'1':12,'2':15,'3':18,'4':21, '5':24, '6':27, '7': 30, '8':33, '9':36, "a":39, 'b':42, 'c':45, 'd':48, 'e':51, 'f':54}
    row_f = loc[2:4]
    print(row_f)
    col_f = loc[4:5]
    print(col_f)
    print(loc)

    #поиск индекса строки, содержащей искомую подстроку
    for i in range(0, 31):
        match = re.findall(f"{row_f}", lines[i][:8], re.IGNORECASE)
        # print(match)
        if not match:
            continue
        else:
            break

    #вычисление остатка для поиска следующего кластера
    if part:
        t_coord = coord[col_f] - 3
        next_claster = lines[i][t_coord:t_coord + 9]
        next_claster = next_claster.split(sep=' ')
        next_claster.reverse()
        next_claster = ''.join(next_claster)
        next_claster = next_claster[0:3]
        print(next_claster)


    else:
        t_coord = coord[col_f]
        next_claster = lines[i][t_coord:t_coord + 9]
        next_claster = next_claster.split(sep=' ')
        next_claster.reverse()
        next_claster = ''.join(next_claster)
        next_claster = next_claster[3:6]
        print(next_claster)


elif zones['1'] == 'FAT16':
    if (offset + number_dir * 1.5)%10!=0:
        part = True
    else:
        part = False

    loc = math.floor(offset + number_dir * 2)
    loc = hex(loc)
    print(loc)
else:
    print()







for i in range(0, 31):
    match = re.findall(f"{file_name[z]}", lines[i], re.IGNORECASE)
    # print(match)
    if not match:
        continue
    else:
        break

