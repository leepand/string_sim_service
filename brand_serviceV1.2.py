# -*- coding: utf-8
"""
model process
"""
import flask_profiler
from flask import Flask, request
from flask import jsonify
import threading
import pandas as pd

ctx = threading.local()
ctx.request = None
import shelve
import flask_profiler
import sim_model
resub_list=[]
import re
import datetime
import time
import os, shutil
from tinydb import TinyDB, Query
from tinydb.operations import set as set_tiny_db
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

DB_PATH = './huangke/brand_db.json'#os.path.join(os.path.dirname(os.path.realpath(__file__)), 'brand_db.json')
TABLE = 'models'
brand_TABLE='Brand_data'
db = TinyDB(DB_PATH)
STORAGE_DIR = './huangke/model_storage/'#os.path.join(os.path.dirname(os.path.realpath(__file__)), 'model_storage/')

Model = Query()

"""
数据插入时间转换
"""
epoch = datetime.datetime.utcfromtimestamp(0)
def convert_dt_to_epoch(dt):
    return (dt - epoch).total_seconds() * 1000.0
import os, shutil
def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text
    else:
        return text.decode('utf-8') 
class meta_info():
    def __init__(self,brand_name,brand_type,status,insert_time):
        self.brand_name = brand_name
        self.brand_type = brand_type
        self.status = status
        self.insert_time=insert_time

def meta_dict(meta_dict,brand_dict,name,b_type,status,time,bid,tree):
    if not pd.isnull(name):
        tree.add(sim_model.resub_string(str(name)+'_'+b_type,resub_list))
        meta_dict['brand_name']=name
        meta_dict['brand_type']=b_type
        meta_dict['status']=status
        meta_dict['last_insert']=time
        meta_dict['brand_id']=bid
        wrong=0
        try:
            brand_dict[safe_unicode(str(name)+'_'+b_type)]=meta_dict
        except:
            wrong+=1
    
        #db.table(brand_TABLE).insert(brand_dict)

class TreeModel:
    def __init__(self):
        self.tree = sim_model.BKTree(sim_model.edit_distance)
        self.brand_info_dict={}
        self.meta_info = {}
        self.recommend={}
        self.recommend_meta={}
    def init(self):
        brand_info = pd.read_excel('./huangke/brand.xlsx', sheetname=0)
        for i in range(len(brand_info['BRANDID'])):
            brand_info_dict_u={}
            brand_info_dict_c={}
            brand_info_dict_e={}
            meta_info_u={}
            meta_info_c={}
            meta_info_e={}
            brand_name_u=brand_info['BRANDNAME'][i]
            brand_name_c=brand_info['BRANDNAMECH'][i]
            brand_name_e=brand_info['BRANDNAMEEN'][i]
            last_insert=convert_dt_to_epoch(datetime.datetime.now())
            meta_dict(meta_info_u,self.brand_info_dict,brand_name_u,'u',brand_info['WORKFLOWSTATUS'][i],last_insert,brand_info['BRANDID'][i],self.tree)
            meta_dict(meta_info_c,self.brand_info_dict,brand_name_u,'c',brand_info['WORKFLOWSTATUS'][i],last_insert,brand_info['BRANDID'][i],self.tree)
            meta_dict(meta_info_e,self.brand_info_dict,brand_name_u,'e',brand_info['WORKFLOWSTATUS'][i],last_insert,brand_info['BRANDID'][i],self.tree)

     


    def insert(self, brand_name,status,brand_type,brand_id):        
        #print('ddddddd:',brand_name)
        meta_info={}
        self.tree.add(sim_model.resub_string(str(brand_name)+'_'+brand_type,resub_list))
        last_insert=convert_dt_to_epoch(datetime.datetime.now())
        meta_info['brand_name']=brand_name
        meta_info['brand_type']=brand_type
        meta_info['status']=status
        meta_info['last_insert']=last_insert
        meta_info['brand_id']=brand_id
        
        self.brand_info_dict[safe_unicode(str(brand_name)+'_'+brand_type)]=meta_info
        #print(self.brand_info_dict)
        #db.table(brand_TABLE).insert(self.brand_info_dict)
        #return self.tree
    def query(self,new_brand_name,N):
       
        recommend={}
        
        c=1
        for dist,brand in list(sorted(set(self.tree.find(new_brand_name, 1))))[:N]:
            print brand
            if dist<0.5:
                recommend_meta={}
                recommend_meta['distance']=dist
                recommend_meta['brand_type']=self.brand_info_dict[safe_unicode(brand)]['brand_type']
                recommend_meta['status']=self.brand_info_dict[safe_unicode(brand)]['status']
                recommend_meta['brand_id']=self.brand_info_dict[safe_unicode(brand)]['brand_id']
                recommend_meta['brand_name']=brand.split('_')[0]
                recommend['top'+str(c)]=recommend_meta
                c+=1
        return recommend
#brand_type:u-inuse,c:china,e:english

model=TreeModel()
t1=time.time()
model.init()
t2=time.time()
print(t2-t1)
print('__init__ done!')
try:
    os.remove('tree.bin')
except:
    pass
    #s = shelve.open('tree.bin')
app = Flask(__name__)
app.config["DEBUG"] = True


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
            result=model.query(newbrand,topk)
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
    app.run(host="127.0.0.1", port=5004)