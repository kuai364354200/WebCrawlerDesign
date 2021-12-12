import sys
import time
import random
import requests
import json
from bs4 import BeautifulSoup
import threading

def go(url):
    try:
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)'}
        html = requests.get(base_url + url, headers=headers).content
        soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')

        # 从id为query的元素里提取value属性，也就是这个词条的名字
        # html是这样的：<input id="query" nslog="normal" nslog-type="10080011" name="word" type="text" autocomplete="off" autocorrect="off" value="中国">
        name = soup.select_one("#title")["data-full-title"]
        # 从class为.abstract_main的元素里提取这个词条的介绍，这里用到text属性然后用strip函数去掉前后的空格
        # 关于.string和.text的区别看下面的链接：https://www.cnblogs.com/gl1573/p/9958716.html
        content = soup.select_one(".abstract").text.strip().replace("\xa0", "")
        # 这一步是找到这个网页里其他词条的链接
        # 先找class为.ed_inner_link的元素,遍历。
        link = soup.select(".ed_inner_link")
        for item in link:
            # 有些a标签不是词条，也就是没有href属性，直接continue跳过
            if "href" not in item.attrs:
                continue

            # 取出a标签的href属性
            href = item["href"]
            # 正常的词条链接：https://baike.baidu.com/item/%E4%B8%AD%E5%9B%BD/1122445
            # 如果这个链接里没有"/item/"，说明这个a标签不是词条
            # 如果这个链接已经在tasks列表或者已经在finishedTasks列表，说明是已经存在的，那就不放进没爬过的链接列表里
            global tasks
            global finishedTasks
            if "/lemma/" in href and href not in tasks and href not in finishedTasks:
                tasks.add(href)
    except:
        global count_1
        print("报错了，不知道啥情况，再爬一次")
        time.sleep(random.randint(0,3))
        return
    data = {"name": name, "url": base_url + url, "content": content}
    print(data)

    # 链接已经爬完了，放进已经爬过的链接列表里
    finishedTasks.add(url)
    #dataset
    global dataset
    dataset.append(data)
    return dataset



# 数据集
dataset = []
# 搜狗百科链接前缀
base_url = "https://baike.sogou.com/"

word_forbidden = ["1"]
f = 'data.txt'
f1='tasks.txt'
f2='finishedTasks.txt'


count_1 = 0
# 没爬过的链接用tasks保存。
with open(f1, "r+", encoding='utf-8') as file:
    tasks = set()
    while True:
        task = file.readline()
        if not task:
            break
        task = task.strip('\n')
        tasks.add(task)
# 爬过的链接用finishedTasks保存


with open(f2, "r+", encoding='utf-8') as file:
    finishedTasks = set()
    while True:
        finishedTask = file.readline()
        if not finishedTask:
            break
        finishedTask = finishedTask.strip('\n')
        finishedTasks.add(finishedTask)

x1 = 1
# 括号中的值为递归深度
sys.setrecursionlimit(1000000)


#当tasks内永远有内容时，就不断执行go函数
while len(tasks) >= 0:
    #如果dataset太长了，就先写入文件，然后清空dataset；
    if len(dataset) >=20:
        # 只需要将之前的”w"改为“a"即可，代表追加内容
        with open(f, "a+", encoding='utf-8') as file:
            for data1 in dataset:
                file.writelines(json.dumps(data1,ensure_ascii=False)+'\n')
        with open(f1, "w+", encoding='utf-8') as file:
            for task in tasks:
                file.write('\n'+str(task))
        with open(f2, "w+", encoding='utf-8') as file:
            for finishedTask in finishedTasks:
                file.write('\n'+str(finishedTask))
        dataset = []
    if word_forbidden == []:
        print("ip被封了")
        break

    # 或者IP被封了导致没的爬了，那就将已经爬过的数据写入txt
    print("第",x1,"次")

    go(tasks.pop())

    x1=x1+1
    if count_1 == 100:
        print("被封ip了")
        break
#如果没有了就告知一声
if len(tasks)==0:
    print("我真的一滴也没有了.jpg")


print("结束了")