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


class TreeModel:
    def __init__(self):
        self.tree = sim_model.BKTree(sim_model.edit_distance)
        self.brand_info_dict={}
        self.meta_info = {}
        self.recommend={}
        self.recommend_meta={}
        
    def insert(self, brand_name,status,brand_type,brand_id):        
        #print('ddddddd:',brand_name)
        self.tree.add(sim_model.resub_string(str(brand_name)+'_'+brand_type,resub_list))
        last_insert=convert_dt_to_epoch(datetime.datetime.now())
        self.meta_info['brand_name']=brand_name
        self.meta_info['brand_type']=brand_type
        self.meta_info['status']=status
        self.meta_info['last_insert']=last_insert
        self.meta_info['brand_id']=brand_id
        
        self.brand_info_dict['brand_index']=str(brand_name)+'_'+brand_type
        self.brand_info_dict['brand_index_info']=self.meta_info
        print(self.brand_info_dict)
        db.table(brand_TABLE).insert(self.brand_info_dict)
        return self.tree
    def query(self,new_brand_name,N):
       
        recommend={}
        
        c=1
        for dist,brand in list(set(sorted(self.tree.find(new_brand_name, 1))))[:N]:
            recommend_meta={}
            #如果brandname+index相同，按插入时间排序，取最近的
            #print db.table(brand_TABLE).search((Model.brand_index == brand))
            #if len(db.table(brand_TABLE).search((Model.brand_index == brand) & (Model.brand_index_info.distance>0.1)))<1:
            #    continue
            query_condition=db.table(brand_TABLE).search((Model.brand_index == brand) & (Model.brand_index_info.status=='APPROVED'))
            count = len(query_condition)
            for i in range(0,count):
                for j in range(i + 1, count):
                    if query_condition[i]['brand_index_info']['last_insert'] < query_condition[j]['brand_index_info']['last_insert']:
                        query_condition[i], query_condition[j] = query_condition[j], query_condition[i]
            #query_condition_sort=query_condition.sort(key=lambda k: (k.get('last_insert', 0)), reverse=True)
            if len(query_condition)<1:
                continue
            recommend_meta['distance']=dist
            recommend_meta['brand_type']=query_condition[0]['brand_index_info']['brand_type']
            recommend_meta['status']=query_condition[0]['brand_index_info']['status']
            recommend_meta['brand_id']=query_condition[0]['brand_index_info']['brand_id']
            recommend_meta['brand_name']=brand.split('_')[0]
            recommend['top'+str(c)]=recommend_meta
            c+=1
        return recommend
#brand_type:u-inuse,c:china,e:english

model=TreeModel()
brand_info = pd.read_excel('./huangke/brand.xlsx', sheetname=0)
for i in range(len(brand_info['BRANDID'])):
    if pd.isnull(brand_info['BRANDNAME'][i]):
        continue
    if pd.isnull(brand_info['BRANDNAMECH'][i]):
        continue
    if pd.isnull(brand_info['BRANDNAMEEN'][i]):
        continue     
    model.insert(brand_info['BRANDNAME'][i],brand_info['WORKFLOWSTATUS'][i],'u',brand_info['BRANDID'][i])
    model.insert(brand_info['BRANDNAMECH'][i],brand_info['WORKFLOWSTATUS'][i],'c',brand_info['BRANDID'][i])
    model.insert(brand_info['BRANDNAMEEN'][i],brand_info['WORKFLOWSTATUS'][i],'e',brand_info['BRANDID'][i])
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