#coding=utf-8
from __future__ import unicode_literals
import gensim
import logging
import sys,os
import numpy
import jieba
import jieba.posseg as pseg

reload(sys)

sys.setdefaultencoding("utf-8")
#导入模型
d = os.path.dirname(os.path.realpath(__file__))

model=gensim.models.Word2Vec.load(os.path.join(d,"word_model/Word60.model"))
logging.basicConfig(format='%(asctime)s: %(levelname)s :%(message)s',filename='my_log.log',level=logging.INFO)


#句式处理
def trim_str(pi_str=""):
    ss=""
    #pi_str=pi_str.encode("utf-8")
    for word in pi_str:
        if word <> " ":
            ss=ss+word
    return ss

#句子重点词汇处理解析
def chuli(pi) :
    question_words=jieba.cut(pi,cut_all=False) #进行分词
    pi=" ".join(question_words).split()
    with open(os.path.join(d,"non_words.txt")) as readme:
        for line in readme:
            non_words=line.split()
            for non_word in non_words:
                for question_word in pi:
                    try:
                        '''排除无关词阈值'''
                        if model.similarity(question_word,non_word)>=0.8:
                            try:
                                pi.remove(question_word)
                            except AttributeError:
                                pass
                    except KeyError:
                        try:
                            tt=model[question_word]
                        except KeyError:
                            try :
                                pi.remove(question_word)
                            except AttributeError:
                                pass
                        else:
                            pass
                    else:
                        pass
    return pi

def get_word_similar(word1,word2):
    try:
        return max(model.similarity(word1,word2),0)
    except KeyError:
        return 0.0

#计算两句话的相似性 单向
def pipei_reverse(s1="",s2=""):
    s1 = chuli(s1)
    s2 = chuli(s2)
    results=[]
    kks=0
    if len(s1)==0:
        return 0
    for s in s1:
        result=0
        for d in s2:
            try:
                result=max(model.similarity(s,d),result)
            except KeyError:
                if d==s:
                    result=1
        results.append(result)
    for kk in results:
        kks=kks+kk
    return kks/len(s1)

#计算两句话的相似性 双向 基于单向
def pipei(s1="",s2=""):
    return (pipei_reverse(s1,s2)+pipei_reverse(s2,s1))/2

#定义增量函数
def zengliang(ss=""):
    with open("kehu.txt","a") as object_file:
        try:
            object_file.write(ss.encode("utf-8")+"\n")
        except UnicodeDecodeError:
            pass

#定义口语到标准的接口
def verbal_to_standard(question_source="",threshold=0.67):
    question=trim_str(question_source)
    ranks=[]
    maybes=[]
    ranks_chushi=[]
    xulie=[]
    #先处理客户的记录
    zengliang_flag=True
    try:
        with open("kehu.txt") as readme:
            for line in readme:
                if line.strip().replace("\n","")==question_source.strip().replace("\n",""):
                    zengliang_flag=False
                    break
    except  IOError:
        pass

    if zengliang_flag:
        zengliang(question_source)

    #开始实现应答
    with open("biaozhun.txt") as file_object:
        ii=0
        for line in file_object:
            '''句子匹配阈值'''
            if pipei(question,line)>=threshold:
                maybes.insert(ii,line)
                ranks.insert(ii,pipei(question,line))
                ii+=1
    ranks_chushi=ranks[:]
    
    for i in range(0,len(ranks)):
        for j in range(i,len(ranks)):
            if ranks[i]<ranks[j]:
                t=ranks[i]
                ranks[i]=ranks[j]
                ranks[j]=t
    #输出可能的结果
    mm=0
    for i in range(0,len(ranks)):
        for j in range(0,len(ranks_chushi)):
            if (ranks_chushi[j]==ranks[i]) and ((ranks[i]<>ranks[i-1] and i<>0) or i==0):
                xulie.insert(mm,j)
                mm+=1

    if len(xulie)>0:
        str_last="您可能想问的是\n"
        for ou in range(0,len(xulie)):
            str_last=str_last+ str(ranks_chushi[xulie[ou]])+" :"+maybes[xulie[ou]]+"\n"
    else:
        str_last="对不起，我不知道您的意思"
    return str_last

#根据标准找口头的接口
def standard_to_verbal(standard="",threshold=0.67):
    standard=trim_str(standard)
    ranks=[]
    maybes=[]
    ranks_chushi=[]
    xulie=[]
    #开始实现应答
    with open("kehu.txt") as file_object:
        ii=0
        for line in file_object:
            '''句子匹配阈值'''
            if pipei(standard,line)>=threshold:
                maybes.insert(ii,line)
                ranks.insert(ii,pipei(standard,line))
                ii+=1
    ranks_chushi=ranks[:]
    for i in range(0,len(ranks)):
        for j in range(i,len(ranks)):
            if ranks[i]<ranks[j]:
                t=ranks[i]
                ranks[i]=ranks[j]
                ranks[j]=t
    #输出可能的结果
    mm=0
    for i in range(0,len(ranks)):
        for j in range(0,len(ranks_chushi)):
            if (ranks_chushi[j]==ranks[i]) and ((ranks[i]<>ranks[i-1] and i<>0) or i==0):
                xulie.insert(mm,j)
                mm+=1
    
    if len(xulie)>0:
        str_last="客户问过的问题可能是:\n"
        for ou in range(0,len(xulie)):
            str_last=str_last+ str(ranks_chushi[xulie[ou]])+" :"+maybes[xulie[ou]]+"\n"
    else:
        str_last="未找到客户可能问过的问题"
    
    return str_last
