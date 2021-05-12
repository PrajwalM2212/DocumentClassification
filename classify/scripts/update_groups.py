import json
from elasticsearch import Elasticsearch

groups_dict = {}

def load_groups():
    with open('id_to_labels.json') as f:
        data = json.load(f)['val']
        for item in data:
            if(groups_dict.get(item[1], 0) == 0):
                groups_dict[item[1]] = [(item[0], item[2])]
            else:
                groups_dict[item[1]].append((item[0], item[2]))
        print(groups_dict)

'''
Updates the group of the documents in elasticsearch
'''
def update_groups():
    es = Elasticsearch()
    for k, v in groups_dict.items():
        for item in v:
            index = ''
            if(item[1] == 'reut2'):
                index = "reut-idx"
            elif item[1] == 'jeopardy':
                index = "jeopardy-idx"
            else:
                index = "xscience-idx"
            print(k, item)
            res = es.update(index, id=item[0], body= {

                "doc": {
                    "group": int(k)
                }

            })
            print(res['result'])
            
if __name__ == '__main__':
    load_groups()
    update_groups()