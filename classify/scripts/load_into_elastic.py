import json
from elasticsearch import Elasticsearch
import xmltodict

'''
Loads rueters data into elasticsearch
'''
def load_rueters():
    j = 0
    es = Elasticsearch()
    for i in range(0, 5):
        with open('data/json-data/reut2-00{}.json'.format(i)) as f:
            data = json.load(f)
            for news_dict in data:
                j = j+1
                print(j)

                del news_dict['attrs']
                del news_dict['companies']
                del news_dict['date']
                del news_dict['dateline']
                del news_dict['exchanges']
                del news_dict['orgs']
                del news_dict['unknown']
                news_dict['group'] = 0
                news_dict['gen_topics'] = []
                news_dict['source'] = 'reut2'
                news_dict['ranking'] = 0
                res = es.index(index="reut-idx", body=news_dict)
                print(res['result'])

'''
Loads jeopardy data into elasticsearch
'''
def load_jeopardy():
    j = 0
    es = Elasticsearch()
    with open('JEOPARDY_QUESTIONS1.json') as f:
        data = json.load(f)
        for qa in data:
            j += 1
            del qa['air_date']
            del qa['round']
            del qa['value']
            del qa['show_number']
            qa['group'] = 0
            qa['gen_topics'] = []
            qa['source'] = 'jeopardy'
            qa['ranking'] = 0
            qa['summary'] = qa['question'] + '\n' + qa['answer']
            res = es.index(index="jeopardy-idx", body=qa)
            print(res)
            if j == 4000:
                break
'''
Loads xscience data into elasticsearch
'''
def load_scientific_arts():
    j = 0
    es = Elasticsearch()
    with open('train.json') as f:
        data = json.load(f)
        for art in data:
            j += 1
            del art['aid']
            del art['mid']
            del art['ref_abstract']
            art['group'] = 0
            art['gen_topics'] = []
            art['source'] = 'multi-xscience'
            art['ranking'] = 0
            res = es.index(index="xscience-idx", body=art)
            print(res)
            if j == 3000:
                break

if __name__ == '__main__':
    load_rueters()
    #res = es.search(index="reut-idx", body={'size' : 1000, "query": {"match_all": {}}})
    load_jeopardy()
    load_scientific_arts()