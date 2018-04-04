import requests
import json

class CCode:  
    def str(self, content, encoding='utf-8'):  
        # 只支持json格式  
        # indent 表示缩进空格数  
        return json.dumps(content, encoding=encoding, ensure_ascii=False, indent=4)  
        pass  
  
    pass  
  


url='http://octopus.wanda.cn:9052/proxy/brand/brandquery?APPKEY=a219eae9aa0a498a91f82fc363298f9f'
data = {"brand_name":"Kailas 肯德基","topk":5}
headers = {'Content-type': 'application/json'}#, 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)

print(r.url)
#print(r.text)   #打印解码后的返回数据
import time

if __name__ == "__main__": 
    t1=time.time()
    cCode = CCode()  
    x=r.json()
    print cCode.str(x) 
    t2=time.time()
    print("request time:%s s"%(t2-t1))



#curl -l -H "Content-type: application/json" -X POST -d '{"brand_name":"\u7c73\u5947","topk":4}' 