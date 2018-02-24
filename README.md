# string_sim_service
Fast Levenshtein distance and BK-tree implementations in Python & Flask.

#### Usage:

Update:

curl -l -H "Content-type: application/json" -X POST -d '{"brand_name":"外国2","status":"active","brand_type":"e"}' http://127.0.0.1:5004/update

Query:

curl -l -H "Content-type: application/json" -X POST -d '{"brand_name":"外国","topk":4}' http://127.0.0.1:5004/query