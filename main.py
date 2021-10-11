import zipfile
import os
import hashlib
import requests
import re
import csv

def unpack_archive(directory_to_extract_to, arch_file):

    arch_file = zipfile.ZipFile(arch_file)
    arch_file.extractall(directory_to_extract_to)
    arch_file.close()

def list_of_txt_files(directory_to_extract_to):

    txt_files = []
    for r, d, f in os.walk(directory_to_extract_to):
        for i in f:
            if ".txt" in i:
                txt_files.append(os.path.join(r, i))
    return txt_files

def MD5_hash(txt_files): #Task 2.2

    for file in txt_files:
        tar_file_data = open(file, "rb")
        data = tar_file_data.read()
        result = hashlib.md5(data).hexdigest()
        tar_file_data.close()
    return result

def find_file_by_hash(target_hash,directory_to_extract_to):

    target_file = ''  # полный путь к искомому файлу
    target_file_data = ''  # содержимое искомого файла
    for r, d, f in os.walk(directory_to_extract_to):
        for i in f:
            file = open(os.path.join(r, i), 'rb').read()
            file_data = hashlib.md5(file).hexdigest()
            if file_data == target_hash:
                target_file = os.path.join(r, i)
                target_file_data = file
    return target_file, target_file_data

def parsing_HTML(target_file_data):

    r = requests.get(target_file_data)
    result_dct = {}
    counter = 0
    lines = re.findall(r'<div class="Table-module_row__3TH83">.*?</div>.*?</div>.*?</div>.*?</div>.*?</div>', r.text)
    for line in lines:
        if counter == 0:
            headers = re.sub(r'<[^<>]*>', ' ', line)
            headers = re.findall("Заболели|Умерли|Вылечились|Активные случаи", headers)
        temp = re.sub(r'<[^<>]*>', ';', line)
        temp = re.sub(r'[*]', '', temp)
        temp = re.sub(r'\(.*?\)', '', temp)
        temp = re.sub(';[;;]*;', ';', temp)
        temp = re.sub(r'^\W+', '', temp)
        temp = re.sub('_', '-1', temp)
        temp = re.sub(r'\xa0', '', temp)
        tmp_split = re.split(';', temp)
        if counter != 0:
            country_name = tmp_split[0]
            col1_val = tmp_split[1]
            col2_val = tmp_split[2]
            col3_val = tmp_split[3]
            col4_val = tmp_split[4]
            result_dct[country_name] = [0, 0, 0, 0]
            result_dct[country_name][0] = int(col1_val)
            result_dct[country_name][1] = int(col2_val)
            result_dct[country_name][2] = int(col3_val)
            result_dct[country_name][3] = int(col4_val)
        counter += 1
    return result_dct,headers

def writing_in_file(result_dct, headers):

    output = open('data.csv', 'w')
    writer = csv.writer(output, delimiter=";")
    writer.writerow(headers)
    for key in result_dct.keys():
        writer.writerow([key, result_dct[key][0], result_dct[key][1], result_dct[key][2], result_dct[key][3]])
    output.close()


if __name__ == '__main__':

    directory_to_extract_to = 'C:\\Users\\User\\Desktop\\Education\\Applic-prog\\1lab' #Task 1
    arch_file = 'C:\\Users\\User\\Downloads\\tiff-4.2.0_lab1.zip'
    os.mkdir(directory_to_extract_to)
    unpack_archive(directory_to_extract_to, arch_file)

    txt_files = list_of_txt_files(directory_to_extract_to) #Task 2.1
    print("Список файлов формата txt: ")
    for i in txt_files:
        print(i)

    result = MD5_hash(txt_files) #Task 2.2
    print("Значения MD5 хеша для найденных файлов: ")
    print(result)

    target_hash = "4636f9ae9fef12ebd56cd39586d33cfb" #Task 3
    target_file, target_file_data = find_file_by_hash(target_hash, directory_to_extract_to)
    print("Полный путь к искомому файлу: ")
    print(target_file)
    print("Содержимое искомого файла: ")
    print(target_file_data)

    result_dct, headers = parsing_HTML(target_file_data) #Task 4

    writing_in_file(result_dct, headers) #Task 5

    target_country = input("Введите название страны: ") #Task 6
    print(result_dct[target_country])

