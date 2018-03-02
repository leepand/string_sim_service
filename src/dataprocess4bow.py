# -*- coding: utf-8 -*-
import jieba
import os
import sys
import pandas as pd
import time
brand_info = pd.read_excel('./huangke/brand.xlsx', sheetname=0)
t1=time.time()
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

def safe_unicode(text):
    """
    Attempts to convert a string to unicode format
    """
    # convert to text to be "Safe"!
    if isinstance(text,unicode):
        return text.encode("utf-8").decode('utf-8') 
    else:
        return text.decode('utf-8') 
def token_single_file(jt,input_fname, output_fname):
    
    ll=len(input_fname['BRANDID'])
    out=open(output_fname, 'w')
    c=0
    for j in range(ll):
        result_lines = []
        result_lines2 = []
        result_lines3 = []
        if not pd.isnull(input_fname['BRANDNAME'][j]):
            try:
                if input_fname['BRANDNAME'][j].encode('utf8')!='无':
                    tokens = jt.tokens(input_fname['BRANDNAME'][j])
                    if len(tokens)<1:
                        continue
                    out.write(u' '.join(tokens).encode('utf8')+'|'+'u'+'|'+str(input_fname['WORKFLOWSTATUS'][j])+\
                              '|'+str(input_fname['BRANDID'][j])+'|'+str(input_fname['BRANDNAME'][j].encode('utf8'))+'\n')
            except:
                #print('wrong')
                c+=1
        
        
        if not pd.isnull(input_fname['BRANDNAMECH'][j]):
            try:
                if input_fname['BRANDNAMECH'][j].encode('utf8')!='无':
                    tokens2 = jt.tokens(input_fname['BRANDNAMECH'][j])
                    if len(tokens2)<1:
                        continue
                    out.write(u' '.join(tokens2).encode('utf8')+'|'+'c'+'|'+str(input_fname['WORKFLOWSTATUS'][j])+\
                              '|'+str(input_fname['BRANDID'][j])+'|'+str(input_fname['BRANDNAMECH'][j].encode('utf8'))+'\n')
            except:
                #print('wrong')
                c+=1

        if not pd.isnull(input_fname['BRANDNAMEEN'][j]):
            try:
                if input_fname['BRANDNAMEEN'][j].encode('utf8')!='无':

                    tokens3 = jt.tokens(input_fname['BRANDNAMEEN'][j])
                    if len(tokens3)<1:
                        continue
                    out.write(u' '.join(tokens3).encode('utf8')+'|'+'e'+'|'+str(input_fname['WORKFLOWSTATUS'][j])+\
                              '|'+str(input_fname['BRANDID'][j])+'|'+str(input_fname['BRANDNAMEEN'][j].encode('utf8'))+'\n')
            except:
                #print('wrong')
                c+=1

    out.close()
    print 'Wrote to ', output_fname,c
jt=JiebaTokenizer('huangke/stopwords.txt')
token_single_file(jt,brand_info,'huangke/jieba_brand_segged.txt')
t2=time.time()
print(t2-t1)