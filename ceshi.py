#-*- coding:utf-8 -*-
import codecs
import sys
from textrank4zh import TextRank4Keyword, TextRank4Sentence

zhaiyao_num = int(sys.argv[1])
text = codecs.open('./context/0015', 'r', 'utf-8').read()
tr4s = TextRank4Sentence(stop_words_file='textrank4zh/stopwords.txt',decay_rate = 1.0)  # 导入停止词
tr4w = TextRank4Keyword(stop_words_file = 'textrank4zh/stopwords.txt')
#使用词性过滤，文本小写，窗口为2
tr4s.analyze(text=text, lower=True, source = 'all_filters')
tr4w.analyze(text=text,lower=True, window=3, pagerank_config={'alpha':0.85})
key = []
print "关键词:"
for item in tr4w.get_keywords(num=10, word_min_len=2):
    key.append(item.word)
print " ".join(key)

def find_in_key(cuts):
    for i in key:
        if cuts.find(i) >= 0:
            return True
    return False

def jianhua(line):
    if len(line) >= 60:
        try:
            line = line.split("，")
            #print "line >50 and len(line) = " + str(len(line))
            for i in range(len(line)):
                if find_in_key(line[i]):
                    if i == 0:
                        return "，".join(line[0:2])
                    else:
                        return "，".join(line[i-1:i+2])
        except:pass
        return line
    else:
        return line

rows_num = tr4s.get_sentences_length()
print "This text is %d rows" %rows_num

count_sentens = 0
print "摘要:"
for item in sorted(tr4s.get_key_sentences(num=rows_num/4),key = lambda x:x.index,reverse = False):
    if float(item.weight) >= 1.0/rows_num and count_sentens <= zhaiyao_num:
        count_sentens += 1
        print jianhua(item.sentence) #type(item.sentence)
    else:
        break

if count_sentens == 0:
    for item in sorted(tr4s.get_key_sentences(num=zhaiyao_num),key = lambda x:x.index,reverse = False):
        print(jianhua(item.sentence))

