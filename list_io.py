from typing import List


def save_2d_list(file_name: str, input_lists: List[list]):
    output_file = open(file_name, "w", encoding="utf-8")
    for input_list in input_lists:
        for s in input_list:
            output_file.write(s)
            output_file.write(' ')
        output_file.write('\n')
    output_file.close()


def load_2d_list(file_name: str):
    output_list = []
    file = open(file_name, "r", encoding="utf-8")
    for line in file:
        inner_list = line.split(' ')
        if inner_list[-1] == '\n':
            inner_list.pop(-1)
        output_list.append(inner_list)
    file.close()
    return output_list


def save_1d_list(file_name: str, input_lists: list):
    output_file = open(file_name, "w", encoding="utf-8")
    for text in input_lists:
        output_file.write(text)
        output_file.write('\n')
    output_file.close()


def load_1d_list(file_name: str):
    output_list = []
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.replace('\n', '')
            output_list.append(line)
    return output_list
