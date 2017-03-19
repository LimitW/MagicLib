#coding=utf-8
import sys
import random
import os

reload(sys)
sys.setdefaultencoding('utf-8')

ff = open('raw_categories.txt', 'r')
f = ff.readlines()
ff.close()

spans = {}
nolist = []
level_spans = []

def add_tag(tag, dic):
    tag = tag.strip()
    if len(tag) < 1:
        return
    if len(tag.split(',')) > 1:
        for i in tag.split(','):
            add_tag(i, dic)
        return
    if dic.get(tag) == None:
        dic[tag] = 1
    else:
        dic[tag] += 1

for line in f:
    idx, cat = line.split('\t')
    idx = idx.strip()
    idx = int(idx)
    cat = cat.strip()
    if len(cat) < 1:
        continue
    if len(cat.split('|')) > 1:
        tags = cat.split('|')
        for tag in tags:
            add_tag(tag, spans)
    elif len(cat.split('>')) > 1:
        tags = cat.split('>')
        cnt = 1
        for tag in tags:
            if len(level_spans) < cnt:
                level_spans.append({})
            add_tag(tag, level_spans[cnt - 1])
            add_tag(tag, spans)
            cnt += 1
    else:
        add_tag(cat, spans)

ff = open('tags.txt', 'wb')
sorted_spans = sorted(spans.iteritems(), key=lambda d:d[1], reverse=True)
for i in sorted_spans:
    ff.write(i[0] + '\t' + str(i[1]) + '\n')
ff.close()

ff = open('level_tags.txt', 'wb')
cnt = 0
for di in level_spans:
    sorted_di = sorted(di.iteritems(), key=lambda d:d[1], reverse=True)
    ff.write('level ' + str(cnt))
    cnt = cnt + 1
    for i in sorted_spans:
        ff.write(i[0] + '\t' + str(i[1]) + '\n')
ff.close()
