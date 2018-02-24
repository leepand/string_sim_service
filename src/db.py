#coding=utf-8
import os
from tinydb import TinyDB, Query
from tinydb.operations import set

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'brand_db.json')
TABLE = 'models'

db = TinyDB(DB_PATH)
STORAGE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'model_storage/')

Model = Query()
"""
 创建模型版本路径
"""
def get_model_dir(name, version=1, create_if_needed=False):
    path = os.path.join(STORAGE_DIR, name, 'v%d' % version)

    if create_if_needed:
        if os.path.exists(path):
            logger.info(Fore.YELLOW,'warning','Model/version path already exists.')
            #print 'Model/version path already exists.'
        else:
            os.makedirs(path)

    return path
def get_all_models():
    return db.table(TABLE).all()

def create_new_model(model_object):
    db.table(TABLE).insert(model_object)

def does_model_exist(name, version):
    return db.table(TABLE).contains((Model.name == name) & (Model.version == version))

def update_model(name, version, updates):
    for update_key, update_val in updates.items():
        db.table(TABLE).update(
            set(update_key, update_val), 
            (Model.name == name) & (Model.version == version))

def get_model(name, version=1):
    if not does_model_exist(name, version):
        return None
    return db.table(TABLE).search((Model.name == name) & (Model.version == version))[0]
def validation_model(name, version=1):
    #if not does_model_exist(name, version):
    #    return None
    return db.table(TABLE).search((Model.name == name) & (Model.version == version))[0]

def delete_model_from_db(name, version=1):
    if does_model_exist(name, version):
        db.table(TABLE).remove((Model.name == name) & (Model.version == version))