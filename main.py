import glob
import math, re, time, os, subprocess
import shlex

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
sectors = []
lines = []
while True:
    file_clasters = input()
    if file_clasters == '':
        break
    else:
        lines.append(file_clasters + '\n')

lines_str = str(lines)

offset = lines[0][0:9]
offset = int(offset, 16)
clasters_list = [file_args['3']]
coord = {'0': 8, '1': 10, '2': 12, '3': 14, '4': 16, '5': 18, '6': 20, '7': 22, '8': 24, '9': 26, "a": 28,
         'b': 30, 'c': 32, 'd': 34, 'e': 36, 'f': 38}

if zones['1'] == 'FAT12':
    if (offset + number_dir * 1.5).is_integer():
        part = False
    else:
        part = True

    for i in range(0, 32):
        lines[i] = lines[i].replace(" ", "")
    loc = math.floor(offset + number_dir * 1.5)
    loc = hex(loc)
    next_loc = loc
    next_clast = 0
    while True:
        if next_clast == 4095:
            break
        else:
            row_f = next_loc[2:4]
            row_f = '00000'+row_f
            print('row ', row_f)
            col_f = next_loc[4:5]
            print('col ', col_f)
            #print(next_loc)
            #поиск индекса строки, содержащей искомую подстроку
            for i in range(0, 31):
                match = re.findall(f"{row_f}", lines[i][0:8], re.IGNORECASE)
                # print(match)
                if not match:
                    continue
                else:
                    break

            #вычисление остатка для поиска следующего кластера
            if part:
                buff = ''
                t_coord = coord[col_f] - 2
                next_clast = lines[i][t_coord:(t_coord + 6)]
                buff += next_clast[4:6]
                buff += next_clast[2:4]
                buff += next_clast[0:2]
                next_clast = buff[0:3]
                print(next_clast)

            else:
                buff = ''
                t_coord = coord[col_f]
                next_clast = lines[i][t_coord:(t_coord + 6)]
                print(next_clast)
                buff += next_clast[4:6]
                print(buff)
                buff += next_clast[2:4]
                print(buff)
                buff += next_clast[0:2]
                print(buff)
                next_clast = buff[3:6]
                print(next_clast)

            next_clast = int(next_clast, 16)

            clasters_list.append(next_clast)

            if (offset + next_clast * 1.5).is_integer():
                part = False
            else:
                part = True

            next_loc = math.floor(offset + next_clast * 1.5)
            next_loc = hex(next_loc)
            print(next_clast)

    print("clasters ",clasters_list)
    if len(clasters_list) > value_of_clasters:

        del clasters_list[-1]

    else:
        print(clasters_list)

    #ШАГ №7

    for i in clasters_list:
        sector = (i - 2) * zones['3'] + pos_start_data
        sectors.append(sector)
        if zones['3'] > 1:
            for x in range(0, zones["3"]-1):
                sector += 1
                sectors.append(sector)
        else:
            continue

    print(f'\033[31mВЫГРУЗИ В ПАПКУ drop_files СЛЕДУЮЩИЕ СЕКТОРА\033[0m')
    for i in range(0, len(sectors)):
        print(sectors[i])

elif zones['1'] == 'FAT16':
    for i in range(0, 32):
        lines[i] = lines[i].replace(" ", "")
    #print(lines)
    loc = math.floor(offset + number_dir * 2)
    loc = hex(loc)
    #print(loc)
    next_loc = loc
    next_clast = 0
    while True:
        if next_clast == 255:
            break
        else:
            row_f = next_loc[2:4]
            #print(row_f)
            col_f = next_loc[4:5]
            #print(col_f)
            #print(next_loc)

            # поиск индекса строки, содержащей искомую подстроку
            for i in range(0, 31):
                match = re.findall(f"{row_f}", lines[i][0:8], re.IGNORECASE)
                # print(match)
                if not match:
                    continue
                else:
                    break

            t_coord = coord[col_f]
            next_clast = lines[i][t_coord:t_coord + 2]
            next_clast = next_clast.split(sep=' ')
            next_clast.reverse()
            next_clast = ''.join(next_clast)
            #next_claster = next_claster[0:2]

            next_clast = int(next_clast, 16)

            clasters_list.append(next_clast)
            next_loc = math.floor(offset + next_clast * 2)
            next_loc = hex(next_loc)
            print(next_clast)
    if len(clasters_list) > value_of_clasters:
        del clasters_list[-1]
    else:
        print(clasters_list)

    #ШАГ №7

    for i in clasters_list:
        sector = (i - 2) * zones['3'] + pos_start_data
        sectors.append(sector)
        if zones['3'] > 1:
            for x in range(0, zones["3"]):
                sector += 1
                sectors.append(sector)

        else:
            continue
    print(f'\033[31mВЫГРУЗИ В ПАПКУ drop_files СЛЕДУЮЩИЕ СЕКТОРА\033[0m')
    for i in range(0, len(sectors)):
        print(sectors[i])
else:
    print("ntfc")

while True:
    if len(os.listdir('drop_file')) < len(sectors):
        continue
    else:
        if len(os.listdir('drop_file')) == len(sectors):
            ans = input("ЗАГРУЗИЛ ВСЕ ФАЙЛЫ?[y/n]")
            if ans == 'y':
                break
            else:
                continue
        else:
            print('ПРИСУТСТВУЮТ ЛИШНИЕ ФАЙЛЫ')
            continue


def rename_files_simple(directory):
    files = [(os.path.join(directory, f), os.path.getctime(os.path.join(directory, f)))
             for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort(key=lambda x: x[1])
    for i, (filepath, _) in enumerate(files):
        os.rename(filepath, os.path.join(directory, str(i + 1)))
        print(f"Renamed {filepath} to {i + 1}")


#Example
rename_files_simple("drop_file")

#subprocess.run(["~/summer.sh", f"{size_dir}"], shell=True)
subprocess.call(shlex.split(f'./summer.sh {size_dir}'))
