# -*- coding: utf-8 -*-

import re
from hashlib import md5
import sys
import jieba.analyse
import threading
import pandas as pd

ctx = threading.local()
ctx.request = None

from scipy.spatial import distance
import numpy as np
import time
import pandas as pd
import datetime
import os, shutil
from annoy import AnnoyIndex
import flask_profiler
from flask import Flask, request
from flask import jsonify
import json
app = Flask(__name__)
app.config["DEBUG"] = True

brand_info = pd.read_excel('./huangke/brand.xlsx', sheetname=0)
"""
数据插入时间转换
"""
epoch = datetime.datetime.utcfromtimestamp(0)
def convert_dt_to_epoch(dt):
    return (dt - epoch).total_seconds() * 1000.0

class Token:

    def __init__(self, hash_list, weight):
        self.hash_list = hash_list
        self.weight = weight

def tokenize(doc):
    doc = filter(None, doc)
    return doc

def md5Hash(token):
    h = bin(int(md5(token.encode("utf-8")).hexdigest(), 16))
    return h[2:]

def hash_threshold(token_dict, fp_len):
    """
    Iterate through the token dictionary multiply the hash lists with the weights
    and apply the binary threshold
    """
    sum_hash = [0] * fp_len
    for _, token in token_dict.items():
        sum_hash = [ x + token.weight * y for x, y in zip(sum_hash, token.hash_list)]

    # apply binary threshold
    for i, ft in enumerate(sum_hash):
        if ft > 0:
            sum_hash[i] = 1
        else:
            sum_hash[i] = 0
    return sum_hash

def binconv(fp, fp_len):
    """
    Converts 0 to -1 in the tokens' hashes to facilitate
    merging of the tokens' hashes later on.
    input  : 1001...1
    output : [1,-1,-1, 1, ... , 1]
    """
    vec = [1] * fp_len
    for indx, b in enumerate(fp):
        if b == '0':
            vec[indx] = -1
    return vec


def calc_weights(terms, fp_len):
    """
    Calculates the weight of each one of the tokens. In this implementation
    these weights are equal to the term frequency within the document.
    :param tokens: A list of all the tokens (words) within the document
    :fp_len: The length of the Simhash values
    return dictionary "my_term": Token([-1,1,-1,1,..,-1], 5)
    """
    term_dict = {}
    for term in terms:
        # get weights
        if term not in term_dict:
            fp_hash = md5Hash(term).zfill(fp_len)
            fp_hash_list = binconv(fp_hash, fp_len)
            token = Token(fp_hash_list, 0)
            term_dict[term] = token
        term_dict[term].weight += 1
    return term_dict

def simhash(doc, fp_len=128):
    """
    :param doc: The document we want to generate the Simhash value
    :fp_len: The number of bits we want our hash to be consisted of.
                Since we are hashing each token of the document using
                md5 (which produces a 128 bit hash value) then this
                variable fp_len should be 128. Feel free to change
                this value if you use a different hash function for
                your tokens.
    :return The Simhash value of a document ex. '0000100001110'
    """
    tokens = tokenize(doc)
    token_dict = calc_weights(tokens, fp_len)
    fp_hash_list = hash_threshold(token_dict, fp_len)
    fp_hast_str = fp_hash_list# ' '.join(str(v) for v in fp_hash_list)
    return fp_hast_str



def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text.encode("utf-8").decode('utf-8') 
    else:
        return text.decode('utf-8') 
#print(len(simhash(safe_unicode('中国'))))
#print simhash('Simhadocumentsh')
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
f = 128
t = AnnoyIndex(f, 'angular')
#if __name__ == '__main__':


def query(newbrand,topk):
    v=simhash(safe_unicode(newbrand))
    item,distances = t.get_nns_by_vector(v, topk, search_k=-1,include_distances=True)
    print item,distances
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
                        
        recommend_meta['distance']=distances[i]
        recommend_meta['brand_type']=brand_dict_info[index]['brand_type']
        recommend_meta['status']=brand_dict_info[index]['status']
        recommend_meta['brand_id']=brand_dict_info[index]['brand_id']
        recommend_meta['brand_name']=brand_dict_info[index]['brand_name']
        recommend['top'+str(i)]=recommend_meta
        print(recommend_meta['brand_name'].encode('utf-8'))
    return recommend
        
        
'''

        last_insert=convert_dt_to_epoch(datetime.datetime.now())
        brand_name_u=brand_info['BRANDNAME'][i]
        brand_name_c=brand_info['BRANDNAMECH'][i]
        brand_name_e=brand_info['BRANDNAMEEN'][i]
    filename_hash = 'hashcode.txt'
    file_to_write = open(filename_hash, 'w+', encoding='utf-8')
    with open(filename, 'r',encoding='utf-8') as file_to_read:
        binary_hash = []
        while True:
            line = file_to_read.readline()  # 整行读取数据
            if not line:
                break
                pass
            line = jieba.analyse.extract_tags(line, 20)
            print(line)
            binary_hash.append(simhash(line))
            file_to_write.writelines(simhash(line))
            file_to_write.write('\n')
    file_to_write.close()
'''
start = time.time()
ll=len(brand_info['BRANDID'])
def meta_dict(index,meta_dict,brand_dict,name,b_type,status,time,bid):
    if not pd.isnull(name):
        meta_dict['brand_name']=name
        meta_dict['brand_type']=b_type
        meta_dict['status']=status
        meta_dict['last_insert']=time
        meta_dict['brand_id']=bid
        wrong=0
        try:
            brand_dict[index]=meta_dict
        except:
            wrong+=1
def simhash_annoy(index,string,meta_info_def,status,brand,b_type):
    kkk=0
    if not pd.isnull(string):
        try:
            vector=simhash(safe_unicode(string))
            if len(vector)==f:
                last_insert=convert_dt_to_epoch(datetime.datetime.now())
                meta_info_def=meta_info_def
                name=string
                b_type=b_type
                status=status
                inserttime=last_insert
                bid=brand
                meta_dict(index,meta_info_def,brand_dict_info,name,b_type,status,inserttime,bid)
                t.add_item(index, vector)
            else:
                print (string,len(vector))
        except:           
            kkk+=1
        

brand_dict_info={}

for j in range(ll):

    meta_info_u={}
    meta_info_c={}
    meta_info_e={}
    simhash_annoy(j,brand_info['BRANDNAME'][j],meta_info_u,brand_info['WORKFLOWSTATUS'][j],brand_info['BRANDID'][j],'u')
    simhash_annoy(j+ll,brand_info['BRANDNAMECH'][j],meta_info_c,brand_info['WORKFLOWSTATUS'][j],brand_info['BRANDID'][j],'c')
    simhash_annoy(j+ll+ll,brand_info['BRANDNAMEEN'][j],meta_info_e,brand_info['WORKFLOWSTATUS'][j],brand_info['BRANDID'][j],'e')

                
                
t.build(10) # 10 trees
t.save('./huangke/brand_tree.ann')
end = time.time()
print(end-start)




@app.route('/update', methods=['POST'])
def update_model():
    ctx.request = request
    #path = request.path_info
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        inputdata=json.loads(json.dumps(request.json))
        print inputdata
        print(type(inputdata))
        brand=safe_unicode(inputdata['brand_name'])
        
        status=inputdata['status']
        brand_type=inputdata['brand_type']
        brand_id=inputdata['brand_id']


        tree=model.insert(brand,status,brand_type,brand_id)
        #s['tree']=tree
        #s.close()
        return jsonify({'success':True,'message':'Successfully activated the model\'s API.\nPlease restart your server for these changes to take effect.'})

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"
    



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
    app.run(host="127.0.0.1", port=5006)