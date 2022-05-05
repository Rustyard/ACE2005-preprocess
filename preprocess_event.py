import os
import random
import xml.etree.ElementTree as ElementTree
from typing import List
from ltp import LTP
import re

from list_io import *

type_dictionary = {
    "Life": 0,
    "Transaction": 1,
    "Movement": 2,
    "Business": 3,
    "Conflict": 4,
    "Contact": 5,
    "Personnel": 6,
    "Justice": 7,
    "Non-event": 8
}

# 在这里指定你的ACE2005语料库存放位置
corpus_dir_bn = os.path.join(os.getcwd(), 'raw/Chinese', 'bn')
corpus_dir_nw = os.path.join(os.getcwd(), 'raw/Chinese', 'nw')
corpus_dir_wl = os.path.join(os.getcwd(), 'raw/Chinese', 'wl')


def load_sgm(source: str, sgm_type: str):
    """
    load a sgm file and extract its texts

    :param source: source file path
    :param sgm_type: type of sgm file, can only be "bn", "nw", or "wl"
    :return: text extracted
    """
    tree = ElementTree.parse(source)
    doc = tree.getroot()

    result_text = ""
    if sgm_type == "bn":
        text_node = doc.find("BODY")[0]
        for turn in text_node.findall("TURN"):
            result_text += turn.text.replace(' ', '').replace('\n', '')
    elif sgm_type == "nw":
        text_node = doc.find("BODY").find("TEXT")
        result_text += text_node.text.replace(' ', '').replace('\n', '')
    elif sgm_type == "wl":
        # 直接以文本方式读取文件，并截取</POSTDATE>和</POST>之间的文本，不使用xml分析
        file = open(source, encoding='utf-8')
        text_all = file.read().replace('\n', '')
        text_start = text_all.find("</POSTDATE>")
        text_end = text_all.find("</POST>")
        if text_start != -1 and text_end != -1:
            # 魔数11 为</POSTDATE>的长度
            result_text += text_all[text_start + 11: text_end].replace(' ', '').replace('\n', '')
    return result_text


def read_xml(path: str) -> List[str]:
    tree = ElementTree.parse(path)
    source_file = tree.getroot()
    assert source_file is not None
    document_node = source_file.find("document")
    assert document_node is not None

    event_list = []

    for e in document_node.findall("event"):
        type_event = e.get("TYPE")
        type_number = type_dictionary[type_event]
        for mention in e.findall("event_mention"):
            event_text = mention.find("extent").find("charseq").text \
                .replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '') # 去除了回车空格等字符，根据需要可以删掉
            event_list.append("%s\t%s" % (event_text, type_number))

    return event_list


# 获取非事件，使用LTP工具进行分句
def get_non_event_list(event_list: List[str]) -> List[str]:
    ltp = LTP()

    # batch process
    data_list = []
    for path, dirs, files in os.walk(corpus_dir_bn):
        for file in files:
            if os.path.splitext(file)[1] == '.sgm':
                text = load_sgm(os.path.join(corpus_dir_bn, file), 'bn')
                data_list.extend(ltp.sent_split([text]))

    for path, dirs, files in os.walk(corpus_dir_nw):
        for file in files:
            if os.path.splitext(file)[1] == '.sgm':
                text = load_sgm(os.path.join(corpus_dir_nw, file), 'nw')
                data_list.extend(ltp.sent_split([text]))

    for path, dirs, files in os.walk(corpus_dir_wl):
        for file in files:
            if os.path.splitext(file)[1] == '.sgm':
                text = load_sgm(os.path.join(corpus_dir_wl, file), 'wl')
                data_list.extend(ltp.sent_split([text]))

    not_event_list = []
    for i, data in enumerate(data_list):
        data = re.sub("[A-Za-z\\(\\)\\[\\]\\.\\_\\/\\“\\”]", "", data) # 除去英文字符及一些其他符号
        if len(data) <= 2:
            continue
        not_event = True
        for j, event in enumerate(event_list):
            if event[:-2] in data:
                not_event = False
                break
        if not_event:
            not_event_list.append('%s\t8' % data)
    return not_event_list


if __name__ == '__main__':
    # batch process
    event_list = []
    for path, dirs, files in os.walk(corpus_dir_bn):
        for file in files:
            if os.path.splitext(file)[1] == '.xml':
                event_list.extend(read_xml(os.path.join(corpus_dir_bn, file)))

    for path, dirs, files in os.walk(corpus_dir_nw):
        for file in files:
            if os.path.splitext(file)[1] == '.xml':
                event_list.extend(read_xml(os.path.join(corpus_dir_nw, file)))

    for path, dirs, files in os.walk(corpus_dir_wl):
        for file in files:
            if os.path.splitext(file)[1] == '.xml':
                event_list.extend(read_xml(os.path.join(corpus_dir_wl, file)))

    # 截掉长度太短的事件
    for event in event_list:
        if len(event[:-2]) <= 2:
            while event in event_list:
                event_list.remove(event)

    non_event_list = get_non_event_list(event_list)
    random.shuffle(non_event_list)
    non_event_list = non_event_list[:400]  # randomly pick 400 non-events
    event_list.extend(non_event_list)
    random.shuffle(event_list) # 随机打乱数据集

    type_size = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0
    }
    for event in event_list:
        index = int(event[-1])
        type_size[index] += 1

    print('Data size:', len(event_list))
    print('size in event type: ')
    print("\tLife:", type_size[0])
    print("\tTransaction", type_size[1])
    print("\tMovement", type_size[2])
    print("\tBusiness", type_size[3])
    print("\tConflict", type_size[4])
    print("\tContact", type_size[5])
    print("\tPersonnel", type_size[6])
    print("\tJustice", type_size[7])
    print("\tNon-event", type_size[8], '\n')
    print('Dividing data as 80% train, 10% dev, 10% test...')
    index_10percent = len(event_list) // 10

    # 在这里修改数据集划分方式
    train_data = event_list[0: -2 * index_10percent]
    dev_data = event_list[-2 * index_10percent: -index_10percent]
    test_data = event_list[-index_10percent:]

    # 在这里修改输出位置
    print("Current directory:", os.getcwd())
    save_1d_list(os.path.join("data", "train.txt"), train_data)
    print("Saved training data as data/train.txt")
    save_1d_list(os.path.join("data", "dev.txt"), dev_data)
    print("Saved dev data as data/dev.txt")
    save_1d_list(os.path.join("data", "test.txt"), test_data)
    print("Saved test data as data/test.txt")
