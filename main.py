import math
import os
import re
import shlex
import subprocess
import pydoc

# МЕТОДИЧКА ПО FAT https://drive.google.com/file/d/19GbO9TWT19yNlAx5nR7CA8Oi0FNyufrg/view
# МЕТОДИЧКА ПО NTFC https://drive.google.com/file/d/1zPc29KquTsB0yoKcUOodIT4ZtslTv-Xy/view
# САЙТ С ФАЙЛОВЫМИ СИСТЕМАМИ https://fat.bk252.ru/

# ШАГ №1
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
results2 = re.search(r'NTFS', lines_str)

zones = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0}

if results is not None:
    if results1 is not None:
        zones['1'] = 'FAT12'
    else:
        zones['1'] = 'FAT16'
else:
    print("NTFS")
    zones['1'] = 'NTFS'

if zones['1'] != 'NTFS':
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

    # ШАГ №3, 4, 5

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
            if not match:
                continue
            else:
                break

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

    # ШАГ №6
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
                row_f = next_loc[2:]
                row_f = row_f[:-1]
                row_f = '00' + row_f
                print('row ', row_f)
                col_f = next_loc[-1]
                print('col ', col_f)

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

        print("clasters ", clasters_list)
        if len(clasters_list) > value_of_clasters:

            del clasters_list[-1]

        else:
            print(clasters_list)

        #ШАГ №7

        for i in clasters_list:
            sector = (i - 2) * zones['3'] + pos_start_data
            sectors.append(sector)
            if zones['3'] > 1:
                for x in range(0, zones["3"] - 1):
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

        loc = math.floor(offset + number_dir * 2)
        loc = hex(loc)

        next_loc = loc
        next_clast = 0
        while True:
            if next_clast == 255 or next_clast == 65535:
                break
            else:
                row_f = next_loc[2:]
                row_f = row_f[:-1]
                row_f = '00' + row_f
                print('row ', row_f)
                col_f = next_loc[-1]
                print('col ', col_f)

                # поиск индекса строки, содержащей искомую подстроку
                for i in range(0, 31):
                    match = re.findall(f"{row_f}", lines[i][0:8], re.IGNORECASE)
                    if not match:
                        continue
                    else:
                        break

                t_coord = coord[col_f]
                next_clast = lines[i][t_coord:t_coord + 4]
                buff = ''
                buff += next_clast[2:4]
                buff += next_clast[0:2]
                print(buff)
                next_clast = buff
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
                for x in range(0, (zones["3"] - 1)):
                    sector += 1
                    sectors.append(sector)

            else:
                continue
        print(f'\033[31mВЫГРУЗИ В ПАПКУ drop_files СЛЕДУЮЩИЕ СЕКТОРА\033[0m')
        for i in range(0, len(sectors)):
            print(sectors[i])

else:
    for i in range(0, 32):
        lines[i] = lines[i].replace(" ", "")

    pos = [[30, 34], [34, 36], [8, 10]]
    numbers = ['2', '3', '4']
    rows = [0, 0, 3]
    i = 0
    for row in rows:
        zone = lines[row]
        if i == 0:
            zone = zone[pos[i][0]:pos[i][1]]
            buff = ''
            buff += zone[2:4]
            buff += zone[0:2]
            zone = buff
            zone = int(zone, 16)
            zones[f'{numbers[i]}'] = zone
            i += 1
        else:
            zone = zone[pos[i][0]:pos[i][1]]
            zone = int(zone, 16)
            zones[f'{numbers[i]}'] = zone
            i += 1

    print('Система хранения                      | ', f'{zones['1']}')
    print('Размер сектора                        | ', f'{zones['2']}', ' байт')
    print('Количество секторов в кластере        | ', f'{zones['3']}', ' сектор')
    print('Cмещение до MFT таблицы в кластерах   | ', f'{zones['4']}', ' секторов')
    offset_mft = int(zones['2']) * int(zones['3']) * int(zones['4'])
    print('Cмещение MFT таблицы                  | ', f'{offset_mft}', ' ')
    print('-----------------------------------------------------------------------')

    start_mft = math.floor(offset_mft / zones['2'])
    print('Сектор корневой папки                 | ', f'{start_mft}', 'сектор')
    print('-----------------------------------------------------------------------')
    mft_table = input(f'\033[31mПЕРЕЙДИ В {start_mft}-Й СЕКТОР И ВСТАВЬ СЮДА ТАБЛИЦУ\033[0m\n')
    lines = []
    while True:
        mft_table = input()
        if mft_table == '':
            break
        else:
            lines.append(mft_table + '\n')
    for i in range(0, 32):
        lines[i] = lines[i].replace(" ", "")

    mft_entry_size = lines[1][32:40]
    buff = ''
    buff += mft_entry_size[6:8]
    buff += mft_entry_size[4:6]
    buff += mft_entry_size[2:4]
    buff += mft_entry_size[0:2]
    mft_entry_size = buff
    offset_root = offset_mft + int(mft_entry_size, 16) * 5
    root_sector = math.floor(offset_root / zones['2'])

    mft_table = input(f'\033[31mПЕРЕЙДИ В {root_sector}-Й СЕКТОР И ВСТАВЬ СЮДА ТАБЛИЦУ\033[0m\n')
    lines = []
    while True:
        mft_table = input()
        if mft_table == '':
            break
        else:
            lines.append(mft_table + '\n')
    for i in range(0, 32):
        lines[i] = lines[i].replace(" ", "")

    offset_present_dir = int(lines[0][0:8], 16)
    offset_attributes = lines[1]
    print(offset_attributes)
    offset_attributes = offset_attributes[16:20]
    print(offset_attributes)
    buff = ''
    buff += offset_attributes[2:4]
    buff += offset_attributes[0:2]
    offset_attributes = int(buff, 16)

    #формула начала таблицы атрибутов
    start_attribute_table = hex(offset_attributes + offset_present_dir)
    print(start_attribute_table)
    col = start_attribute_table[-1]
    col = (int(col, 16) * 2) + 8

    row = '00' + start_attribute_table[2:5]

    z = 0
    for i in range(0, 31):
        match = re.findall(f"{row}", lines[i], re.IGNORECASE)
        if not match:
            z += 1
            continue
        else:
            break

    #первые 4 байта - идентификатор атрибута, на этом шаге нужен атрибут А0
    first_attribute_bites = lines[z][col:(col + 8)]
    print(first_attribute_bites)
    # вторые 4 байта - размер атрибута, его мы прибавляем к началу таблицу атрибутов
    second_attribute_bites = lines[z][(col + 8):(col + 16)]
    buff = ''
    buff += second_attribute_bites[6:8]
    buff += second_attribute_bites[4:6]
    buff += second_attribute_bites[2:4]
    buff += second_attribute_bites[0:2]
    second_attribute_bites = buff
    print(second_attribute_bites)
    next_offset = start_attribute_table
    while True:
        if first_attribute_bites[0:2] == 'A0':
            break
        else:
            next_offset = hex(int(next_offset, 16) + int(second_attribute_bites, 16))
            print(next_offset)
            row = '00' + next_offset[2:5]
            col = next_offset[-1]
            col = (int(col, 16) * 2) + 8
            z = 0
            for i in range(0, 31):
                match = re.findall(f"{row}", lines[i], re.IGNORECASE)
                if not match:
                    z += 1
                    continue
                else:
                    break
            first_attribute_bites = lines[z][col:(col + 8)]
            second_attribute_bites = lines[z][(col + 8):(col + 16)]
            buff = ''
            buff += second_attribute_bites[6:8]
            buff += second_attribute_bites[4:6]
            buff += second_attribute_bites[2:4]
            buff += second_attribute_bites[0:2]
            second_attribute_bites = buff
            print(first_attribute_bites[0:2])

    #идентификатор атрибута
    ident = first_attribute_bites[0:2]
    #флаг нерезидентности
    residence_flag = lines[z][(col + 16):(col + 18)]
    #смещение до списка серий от начала атрибута
    offset_series = lines[z + 2][col:(col + 4)]
    buff = ''
    buff += offset_series[2:4]
    buff += offset_series[0:2]
    offset_series = buff
    #размер данных
    size_data = lines[z + 3][col:(col + 8)]
    buff = ''
    buff += size_data[6:8]
    buff += size_data[4:6]
    buff += size_data[2:4]
    buff += size_data[0:2]
    size_data = buff
    next_offset = hex(int(next_offset, 16) + int(offset_series, 16))
    z = 0
    row = '00' + next_offset[2:5]
    col = next_offset[-1]
    col = (int(col, 16) * 2) + 8
    for i in range(0, 31):
        match = re.findall(f"{row}", lines[i], re.IGNORECASE)
        if not match:
            z += 1
            continue
        else:
            break
    #список серий
    list_of_series = lines[z][col:(col + 2)]

    a = hex(int(list_of_series[0:1]) + int(list_of_series[-1], 16))
    list_of_series = lines[z][col:(col + 2 + int(a[2:]) * 2)]
    print("list of series", list_of_series)

    c = int(list_of_series[1:2]) * 2
    b = c + int(list_of_series[0:1]) * 2

    #колво занимаемых областью данных кластеров
    value_of_clast = list_of_series[2:(2 + c)]

    #смещение до области данных
    offset_data_area = list_of_series[(2 + c):(2 + b)]

    buff = ''
    buff += offset_data_area[2:4]
    buff += offset_data_area[0:2]
    offset_data_area = buff

    #смещение области данных на таблицу индексов
    offset_index_area = zones['2'] * zones['3'] * int(offset_data_area, 16)

    #сектор области данных на таблицу индексов
    index_sector = zones['3'] * int(offset_data_area, 16)

    index_table = input(f'\033[31mПЕРЕЙДИ В {index_sector}-Й СЕКТОР И ВСТАВЬ СЮДА ТАБЛИЦУ\033[0m\n')
    lines = []
    while True:
        index_table = input()
        if index_table == '':
            break
        else:
            lines.append(index_table + '\n')
    for i in range(0, 32):
        lines[i] = lines[i].replace(" ", "")


    #смещение таблицы индексов
    offset_index_table = int(lines[0][0:8], 16)
    print('offset_index_table', offset_index_table)

    offset_markers = lines[0][16:20]
    buff = ""
    buff += offset_markers[2:4]
    buff += offset_markers[0:2]

    #смещение до списка маркеров
    offset_markers = buff
    value_of_markers = lines[0][20:24]
    buff = ""
    buff += value_of_markers[2:4]
    buff += value_of_markers[0:2]

    #количество маркеров в списке
    value_of_markers = buff

    #смещение до начала данных таблицы индексов
    offset_start_index = (offset_index_table + int(offset_markers, 16) + int(value_of_markers) * 2)
    print('offset_start_index_1', offset_start_index)
    s = 1
    while True:
        if offset_start_index / 8 == int(offset_start_index / 8):
            break
        else:
            offset_start_index = (offset_index_table + int(offset_markers, 16) + (int(value_of_markers) + s) * 2)
            s += 1

    offset_start_index = hex(offset_start_index)
    print('offset_start_index_2', offset_start_index)
    row = offset_start_index[2:-1]
    col = offset_start_index[-1]
    col = (int(col, 16) * 2) + 8
    z = 0
    for i in range(0, 31):
        match = re.findall(f"{row}", lines[i], re.IGNORECASE)
        if not match:
            z += 1
            continue
        else:
            break
    print(offset_start_index)
    #смеще
    offset_current = lines[z][col:(col + 4)]
    print(offset_current)
    offset_next_index = lines[z][col+16:col+18]
    

print("КОГДА ЗАГРУЗИШЬ ВСЕ ФАЙЛЫ, ВВЕДИ ЛЮБОЕ ЗНАЧЕНИЕ")
a = input()


def rename_files_simple(directory):
    files = [(os.path.join(directory, f), os.path.getctime(os.path.join(directory, f)))
             for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort(key=lambda x: x[1])
    for i, (filepath, _) in enumerate(files):
        os.rename(filepath, os.path.join(directory, str(i + 1)))
        print(f"Renamed {filepath} to {i + 1}")


# Example
rename_files_simple("drop_file")
subprocess.call(shlex.split(f'./summer.sh {size_dir}'))
