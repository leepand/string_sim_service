# string_sim_service
Fast doc2vec and similarity computation  implementations in Python & Flask.

#### Usage:

Update:

curl -l -H "Content-type: application/json" -X POST -d '{"brand_name":"外国2","status":"active","brand_type":"e"}' http://127.0.0.1:5004/update

Query:

curl -l -H "Content-type: application/json" -X POST -d '{"brand_name":"米奇","topk":4}' http://127.0.0.1:5007/query

Response：

```
http://127.0.0.1:5007/query
{
    "success": true, 
    "recommend": {
        "top9": {
            "brand_type": "e", 
            "brand_id": "1025684", 
            "status": "approved", 
            "brand_name": "米奇family", 
            "distance": "0.29289323"
        }, 
        "top8": {
            "brand_type": "c", 
            "brand_id": "1025684", 
            "status": "approved", 
            "brand_name": "米奇family", 
            "distance": "0.29289323"
        }, 
        "top7": {
            "brand_type": "u", 
            "brand_id": "1025684", 
            "status": "approved", 
            "brand_name": "米奇family", 
            "distance": "0.29289323"
        }, 
        "top6": {
            "brand_type": "c", 
            "brand_id": "1030379", 
            "status": "approved", 
            "brand_name": "开心米奇", 
            "distance": "0.29289323"
        }, 
        "top5": {
            "brand_type": "u", 
            "brand_id": "1030379", 
            "status": "approved", 
            "brand_name": "开心米奇", 
            "distance": "0.29289323"
        }, 
        "top4": {
            "brand_type": "c", 
            "brand_id": "1011653", 
            "status": "approved", 
            "brand_name": "米奇生活馆", 
            "distance": "0.29289323"
        }, 
        "top3": {
            "brand_type": "u", 
            "brand_id": "1011653", 
            "status": "approved", 
            "brand_name": "米奇生活馆", 
            "distance": "0.29289323"
        }, 
        "top2": {
            "brand_type": "u", 
            "brand_id": "100011674", 
            "status": "approved", 
            "brand_name": "米奇", 
            "distance": "0.0"
        }, 
        "top1": {
            "brand_type": "c", 
            "brand_id": "1026695", 
            "status": "approved", 
            "brand_name": "米奇", 
            "distance": "0.0"
        }, 
        "top0": {
            "brand_type": "u", 
            "brand_id": "1026695", 
            "status": "approved", 
            "brand_name": "米奇", 
            "distance": "0.0"
        }
    }
}
request time:0.00137090682983 s
```