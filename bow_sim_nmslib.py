# -*- coding: utf-8 -*-
# query for the nearest neighbours of the first datapoint
import jieba
import threading
ctx = threading.local()
ctx.request = None
import flask_profiler
from flask import Flask, request
from flask import jsonify
import json
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import os
import tempfile
from six import iteritems
from gensim import corpora
import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

TEMP_FOLDER = tempfile.gettempdir()
print('Folder "{}" will be used to save temporary dictionary and corpus.'.format(TEMP_FOLDER))


# collect statistics about all tokens
dictionary = corpora.Dictionary(line.lower().split('|')[0].split() for line in open('huangke/jieba_brand_segged.txt'))

stoplist=[]
# remove stop words and words that appear only once
stop_ids = [dictionary.token2id[stopword] for stopword in stoplist 
            if stopword in dictionary.token2id]
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq < 1]

# remove stop words and words that appear only once
dictionary.filter_tokens(stop_ids + once_ids)
print(dictionary)
#处理训练数据-dictionary & sparse vector
def meta_dict_info(meta_dict,name,b_type,status,time,bid):
    meta_dict['brand_name']=name
    meta_dict['brand_type']=b_type
    meta_dict['status']=status
    meta_dict['last_insert']=time
    meta_dict['brand_id']=bid
    return meta_dict
"""
数据插入时间转换
"""
epoch = datetime.datetime.utcfromtimestamp(0)
def convert_dt_to_epoch(dt):
    return (dt - epoch).total_seconds() * 1000.0
index2info={}
#创建最近邻索引
# Set index parameters
# These are the most important onese
M = 30
efC = 100

num_threads = 4
index_time_params = {'M': M, 'indexThreadQty': num_threads, 'efConstruction': efC, 'post' : 0}

import time
t1=time.time()
import nmslib
'''BowTree'''
class MyCorpus(object):
    def __init__(self):
        self.vector2dict={}
    def train(self):
        index = nmslib.init(method='sw-graph', space='cosinesimil_sparse', data_type=nmslib.DataType.SPARSE_VECTOR)
        _index=0
        for i,line in enumerate(open('huangke/jieba_brand_segged.txt')):
            meta_dict2={}
            v=dictionary.doc2bow(line.lower().split('|')[0].split())
            lenv=len(dictionary.doc2bow(line.lower().split('|')[0].split()))
            if lenv==0:
                print line.lower().split('|')[4:][0].split('\n')[0],i
            if lenv>0:
                #print _index,v
                #continue
                brand_type=line.lower().split('|')[1]
                status=line.lower().split('|')[2]
                brand_id=line.lower().split('|')[3]
                name=line.lower().split('|')[4:][0].split('\n')[0]
                last_insert=convert_dt_to_epoch(datetime.datetime.now())
                #print(i,meta_dict2,name,brand_type,status,last_insert,brand_id,v)
                index2info[i]=meta_dict_info(meta_dict2,name,brand_type,status,last_insert,brand_id)
                index.addDataPoint(i,v)
                _index+=1
        index.createIndex()#{'post': 1}, print_progress=True)
        return index,index2info
        # assume there's one document per line, tokens separated by whitespace
        #yield dictionary.doc2bow(line.lower().split('|')[0].split())
index_tree,indexinfo = MyCorpus().train() # doesn't load the corpus into memory!

'''EditTree'''






t2=time.time()
print(t2-t1)



def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text.encode("utf-8").decode('utf-8') 
    else:
        return text.decode('utf-8') 
class JiebaTokenizer:
    def __init__(self, stop_words_path, mode='m'):
        self.stopword_set = set()
        # load stopwords
        with open(stop_words_path) as ins:
            for line in ins:
                self.stopword_set.add(line.strip().decode('utf8'))
        self.mode = mode

    def tokens(self, intext):
        intext = u' '.join(intext.split())
        if self.mode == 's':
            token_list = jieba.cut_for_search(intext)
        else:
            token_list = jieba.cut(intext)
        return [token for token in token_list if token.strip() != u'' and not token in self.stopword_set]
def query(newbrand,topk):
    new_doc = newbrand
    jt=JiebaTokenizer('huangke/stopwords.txt')
    tokens = jt.tokens(safe_unicode(new_doc))
    new_doc=u' '.join(tokens).encode('utf8')
    new_vec = dictionary.doc2bow(new_doc.lower().split())
    #print(new_vec)  # the word "interaction" does not appear in the dictionary and is ignored
    item, distances = index_tree.knnQuery(new_vec, k=topk)
    #print item,distances
    recommend={}
    if len(item)<1:
        return 'None'
    if len(item)<topk:
        n=len(item)
    else:
        n=topk
    for i in range(n):
        recommend_meta={}
        
        index = item[i]
                        
        recommend_meta['distance']=str(distances[i])
        recommend_meta['brand_type']=indexinfo[index]['brand_type']
        recommend_meta['status']=indexinfo[index]['status']
        recommend_meta['brand_id']=indexinfo[index]['brand_id']
        recommend_meta['brand_name']=indexinfo[index]['brand_name']
        recommend['top'+str(i)]=recommend_meta
        print(recommend_meta['brand_name'].decode('utf-8')),recommend
    return recommend

#new_doc = u"肯德基"
#print new_doc.lower().split()

@app.route('/query', methods=['POST'])
def recommend():
    #model2=TreeModel()
    ctx.request = request
    #path = request.path_info
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        inputdata=json.loads(json.dumps(request.json))
        #print(inputdata['update'])
        update=3
        if update<2:#inputdata['update']:
            brand=safe_unicode(inputdata['brand_name'])
        
            status=inputdata['status']
            brand_type=inputdata['brand_type']
            model.insert(brand,status,brand_type)
            return jsonify({'success':True,'message':'Successfully activated the model\'s API.\nPlease restart your server for these changes to take effect.'})
        else:
            newbrand=inputdata['brand_name']
            print inputdata
            topk=inputdata['topk']
            print newbrand,topk
            result=query(newbrand,topk)
            return jsonify({'success':True,'recommend':result})

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"



app.config['flask_profiler']={"enabled": True,"storage": {"engine": "mongodb"},"basicAuth":{"enabled": True,"username": "leepand","password":"admin"},"ignore": ["^/static/.*"]}
flask_profiler.init_app(app)
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5007)