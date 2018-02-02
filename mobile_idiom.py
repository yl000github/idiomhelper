'''
针对微信小程序，成语消消看，思路
1.读取题目，ocr识别获取所有文字
2.遍历文字列表，查找匹配，找出一个匹配项则删除
3.直至找出所有成语
4.输出

人手工填
'''

import subprocess
import os
from PIL import Image
import json
import pymysql
def get_pic():
    os.system('adb shell screencap -p /sdcard/idiom.png')
    os.system('adb pull /sdcard/idiom.png .')
    return 'idiom.png'

def ocr(path):
    image = Image.open(path)
    question_im = image.crop((39, 269, 1040, 1160))
    crop_path='crop_'+path
    question_im.save(crop_path)
    with open(crop_path,'rb') as f:
        APP_ID = ''
        API_KEY = ''
        SECRET_KEY = ''
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        image=f.read()
        print('开始百度ocr文字识别')
        options = {}
        options["language_type"] = "CHN_ENG"
        data=client.basicGeneral(image,options)
        print('识别结果为',data)
        obj=data
        str=''
        for words in obj['words_result']:
            str+=words['words']
            
#         str='致|兴|尘|仆|迢|千|彬步‖|有|苍|气|迢礼|勃|金|冲|怒勃彬|里|步||闪|风|光机白苍|勃|冲||升发|闪|勃|仆|生'
#         str='致|兴|尘|仆|迢|千|彬步‖济|有济|苍|气|迢礼|勃|金|冲|怒勃彬|里|步|人|闪|风|光机白苍|勃|冲|才|升发|闪|勃|仆|生'
#         str='人致|兴'
        print('抽取的所有文本 ===',str)
        fil_str=''
        for uchar in str:
            if uchar >= '\u4e00' and uchar<='\u9fa5':
                fil_str+=uchar
        print('筛选后的所有文本 ===',fil_str)
        obj={}
        for w in fil_str:
            if w in obj:
                obj[w]+=1
            else:
                obj[w]=1   
        return obj

def find_idiom(words):
    '''

    '''
    print('\n\n\n\n=====匹配阶段=====')
    cys=db_match(words)
    print('目标字',[w for w in words])
    print('目标成语',cys)
    print('目标成语数量',len(cys))
    for cy in cys:
        flag=1
        for w in cy:
            if w not in words:
                flag=0
            else:
                words[w]-=1
                if words[w]<0:
                    flag=0
#         还原
        if flag==0:
#             失败的加回去
            for w in cy:
                if w in words:
                    words[w]+=1
        else:
            val=input("成语  %s 是否要?y/n"%(cy))
            print(val)
            if val!='n':
#             成功的消0
                yield cy
                for w in cy:
                    if w in words and words[w]==0:
                        words.pop(w)
            else:
                for w in cy:
                    if w in words:
                        words[w]+=1
    print('最终无法匹配的字为',words)
        
    
    return words


glo_con=None
def getCon():
    global glo_con
    config = {
          'host':'localhost',
          'port':3306,
          'user':'root',
          'passwd':'123456',
          'db':'idiom',
          'charset':'utf8',
          'cursorclass':pymysql.cursors.DictCursor,
    }
    if glo_con is None:
        con=pymysql.connect(**config)
    return con    
def db_match(words):
    con=getCon()
    cur=con.cursor()
#     cur.execute('select name from cy where name like "%{}%" and LENGTH(name)=12'.format((first_word)))
    sql='select DISTINCT name from cy where LENGTH(name)=12 and (%s)'%(' or '.join(['name like "%{}%"'.format((w)) for w in words]))
    print('执行的sql为',sql)
    cur.execute(sql)
    rs=cur.fetchall()
    print('数据库查询的结果',rs)
    l=[]
    for item in rs:
        l.append(item['name'])
    return l    
    
path=get_pic()
words=ocr(path)
idiom_list=find_idiom(words)
print('最终的匹配的成语为：',[idiom for idiom in idiom_list])