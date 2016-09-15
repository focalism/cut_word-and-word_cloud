

#-*- coding: utf-8 -*-
"""
Minimal Example
===============
Generating a square wordcloud from the US constitution using default arguments.
"""
import matplotlib.pyplot as plt
from os import path
import numpy as np
import random
from PIL import Image
from wenben_fenci import wenben_content
from wordcloud import WordCloud
def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)

d = path.dirname(__file__)
frequencies = wenben_content.content

#wordcloud = WordCloud(font_path='./simhei.ttf',max_font_size=40, relative_scaling=.5).fit_words(frequencies)
pic_path = np.array(Image.open('./test_pic.jpg'))
wordcloud = WordCloud(font_path='./simhei.ttf',margin=10, max_words=2000,mask=pic_path).fit_words(frequencies)
default_colors = wordcloud.to_array()
plt.title("Custom colors")
plt.imshow(wordcloud.recolor(color_func=grey_color_func,random_state=3))
wordcloud.to_file('./a_new_hope.png')
plt.axis("off")
plt.figure()
plt.title("Default colors")
plt.imshow(default_colors)
plt.axis("off")
plt.show()

#plt.figure()
#plt.imshow(wordcloud)
plt.axis("off")
plt.show()
