#!/usr/bin/env python
import re
import random
import numpy as np
from PIL import Image
from pickle import load,dump
import matplotlib.pyplot as plt
from wordcloud import WordCloud

#读取文本内容
def read_txt(url):
    text = ''
    file = open(url,'r')
    for line in file:
        line = line.strip()
        text += line
    return text

#去掉标点等其他符号
def re_sub(sent):
    sent = re.sub("[\s+\.\!\/_,$);:?\]\[}{%^*(+\"\']+|[+——！，。？・～`、@#￥%&*（）《》；……”：‘’“『』【】]+|[0-9a-zA-Z]+","",sent)
    return sent

def n_fenci(url):
    sent = read_txt(url)
    sent = re_sub(sent)
    word_lists = []
    for i in range(len(sent)):
        word_lists.append(sent[i:i+1])
        word_lists.append(sent[i:i+2])
        word_lists.append(sent[i:i + 3])
        word_lists.append(sent[i:i + 4])
        #word_lists.append(sent[i:i + 5])
    return sent,word_lists

def word_fre(word_lists):
    word_num = {}
    for word in word_lists:
        if word not in word_num:
            word_num[word] = 1
        else:
            word_num[word] += 1
    return word_num
#

def cal_word_pro(word_num,text):
    word_probablity = {}
    word_adhes = {}
    left_word = {}
    right_word = {}
    all_word_num = sum(list(word_num.values()))
    for key in list(word_num.keys()):
        word_probablity[key] = word_num[key]/all_word_num
    for key in list(word_probablity.keys()):
        if len(key)>=2:
            left_word[key] = re.findall('(.?){1}%s'%key,text)
            right_word[key] = re.findall('%s(.?){1}'%key,text)
        if len(key) == 2:
            word_adhes[key] = word_probablity[key]/(word_probablity[key[0:1]]*word_probablity[key[1:2]])

        if len(key) == 3:
            word_adhes[key] = min(word_probablity[key]/(word_probablity[key[0:1]]*word_probablity[key[1:3]]),
                             word_probablity[key]/(word_probablity[key[0:2]]*word_probablity[key[2:3]]))
        if len(key) == 4:
            word_adhes_1_3 = word_probablity[key]/(word_probablity[key[0:1]]*word_probablity[key[1:4]])
            word_adhes_3_1 = word_probablity[key]/(word_probablity[key[0:3]]*word_probablity[key[3:4]])
            word_adhes_2_2 = word_probablity[key]/(word_probablity[key[0:2]]*word_probablity[key[2:4]])
            word_adhes[key] = min(word_adhes_1_3,word_adhes_3_1,word_adhes_2_2)
        """
        if len(key) == 5:
            word_adhes_1_3 = word_probablity[key]/(word_probablity[key[0:1]]*word_probablity[key[1:5]])
            word_adhes_3_1 = word_probablity[key]/(word_probablity[key[0:4]]*word_probablity[key[4:5]])
            word_adhes_2_3 = word_probablity[key]/(word_probablity[key[0:2]]*word_probablity[key[2:5]])
            word_adhes_3_2 = word_probablity[key] / (word_probablity[key[0:3]] * word_probablity[key[3:5]])
            word_adhes[key] = round(min(word_adhes_1_3,word_adhes_3_1,word_adhes_2_3,word_adhes_3_2),2)
        """
    return left_word,right_word,word_adhes


def get_Neighborhood_dict(dict):
    new_word_dict = {}
    for key in list(dict.keys()):
        new_word_dict[key] = {}
        for word in dict[key]:
            if word not in new_word_dict[key]:
                new_word_dict[key][word] = 1
            else:
                new_word_dict[key][word] += 1
    return new_word_dict

def cal_Entropy(dict):
    Entropy = {}
    for key in list(dict.keys()):
        Entropy[key] = 0
        for newkey in dict[key]:
            total = sum(list(dict[key].values()))
            Entropy[key] += -(dict[key][newkey]/total)*np.log10(dict[key][newkey]/total)
        Entropy[key] = round(Entropy[key],4)
    return Entropy

def get_Entropy_wordadhes(word_num,text):
    Entropy = {}
    left_word, right_word, word_adhes = cal_word_pro(word_num, text)
    left_word_dict = get_Neighborhood_dict(left_word)
    right_word_dict = get_Neighborhood_dict(right_word)
    lef_Entropy = cal_Entropy(left_word_dict)
    right_Entropy = cal_Entropy(right_word_dict)
    for key in lef_Entropy:
        Entropy[key] = (min((lef_Entropy[key], right_Entropy[key])))
    return Entropy,word_adhes
def del_in_word(dict):
    for key in list(dict.keys()):
        if len(key) == 3:
            if key[0:2] in dict or key[1:3] in dict:
                del dict[key]
        if len(key) == 4:
            if key[0:2] in dict or key[1:3] in dict or  key[2:4] in dict or key[0:3] in dict or key[1:4] in dict:
                del dict[key]
    return dict

def get_cut_dict():
    cut_dict = {}
    file = open('result.txt', 'w+')
    try:
        word_num = load(open('word_num_cache.pickle','rb'))
        word_adhes = load(open('word_adhes.pickle','rb'))
        Entropy = load(open('Entropy_cache.pickle','rb'))
    except:
        text,word_list = n_fenci('text.txt')
        word_num = word_fre(word_list)
        Entropy,word_adhes = get_Entropy_wordadhes(word_num,text)
        dump(word_num, open('word_num_cache.pickle', 'wb'))
        dump(word_adhes,open('word_adhes.pickle','wb'))
        dump(Entropy,open('Entropy_cache.pickle','wb'))
    for key in list(word_num.keys()):
        if len(key)==2:
            if word_num[key]>=4 and word_adhes[key]>200 and Entropy[key]>0.1:
                if key not in cut_dict:
                    cut_dict[key] = word_num[key]
        if len(key) == 3:
            if word_num[key] >= 2 and Entropy[key] > 0.1 and word_adhes[key]>=500:
                if key not in cut_dict:
                    cut_dict[key] = word_num[key]
        if len(key) == 4:
            if word_num[key] >= 2 and Entropy[key] > 0.1 and word_adhes[key] >= 500:
                if key not in cut_dict:
                    cut_dict[key] = word_num[key]

        """
        if len(key) == 5:
            if word_num[key] >= 1 and Entropy[key] > 0.1 and word_adhes[key] >= 500:
                if key not in cut_dict:
                    cut_dict[key] = word_num[key]
                print('word=' + key + '\t' + 'adhes=' + str(word_adhes[key]) + '\t' + 'entropy=' + str(Entropy[key]) + '\t' + 'nums=' + str(word_num[key]))
        """
    cut_dict = del_in_word(cut_dict)
    cut_dict = sorted(cut_dict.items(),key = lambda x:x[1],reverse=True)
    keys = []
    for item in cut_dict:
        key = item[0]
        keys.append(key)
        file.write('word=' + key + '\t' + 'nums=' + str(word_num[key]) + '\t' + 'adhes=' + str(
            int(word_adhes[key])) + '\t' + 'entropy=' + str(Entropy[key]) + '\n')
    return cut_dict

def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

def word_cloud():
    frequencies = get_cut_dict()
    pic_path = np.array(Image.open('./test_pic.jpg'))
    wordcloud = WordCloud(background_color='white',font_path='./simhei.ttf', margin=10, max_words=2000, mask=pic_path).fit_words(frequencies)
    default_colors = wordcloud.to_array()
    plt.title("Custom colors")
    plt.imshow(wordcloud.recolor(color_func=grey_color_func, random_state=3))
    wordcloud.to_file('./a_new_hope.png')
    plt.axis("off")
    plt.figure()
    plt.title("Default colors")
    plt.imshow(default_colors)
    plt.axis("off")
    plt.show()
    plt.axis("off")
    plt.show()

word_cloud()




