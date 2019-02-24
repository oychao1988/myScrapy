import json

from jsonpath import jsonpath


with open('zitems.json', 'r') as f:
    # json_str = f.read()
    json_dict = json.load(f)

# print(json_dict)
result = jsonpath(json_dict, '$.data.results')[0]
print(type(result))
[print(each) for each in result]