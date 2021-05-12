from flask import Blueprint, request
from elasticsearch import Elasticsearch
from joblib import load, dump
from .scripts import classify_docs
from .scripts import update_groups
from .scripts import rank_documents
from sklearn.feature_extraction.text import TfidfVectorizer
from numpyencoder import NumpyEncoder
import json
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

'''
API endpoint to insert new data
<index> is the index to which the new data has to be inserted into
'''
@bp.route('/insert/<index>',  methods = ['POST'])
def insert_into_elastic(index):
    es = Elasticsearch()
    data = request.json
    res1 = {}
    if index == 'reut-idx':
        del data['attrs']
        del data['companies']
        del data['date']
        del data['dateline']
        del data['exchanges']
        del data['orgs']
        del data['unknown']
        data['group'] = 0
        data['gen_topics'] = []
        data['source'] = 'reut2'
        data['ranking'] = 0
        try:
            res1 = es.index(index="reut-idx", body=data)
        except Exception as e:
            return {"error": 'Error while inserting data to elasticsearch'}
    elif index == 'jeopardy-idx':
        del data['air_date']
        del data['round']
        del data['value']
        del data['show_number']
        data['group'] = 0
        data['gen_topics'] = []
        data['source'] = 'jeopardy'
        data['ranking'] = 0
        data['summary'] = data['question'] + '\n' + data['answer']
        try:
            res1 = es.index(index="jeopardy-idx", body=data)
        except Exception as e:
            return {"error": 'Error while inserting data to elasticsearch'}
    elif index == 'xscience-idx':
        del data['aid']
        del data['mid']
        del data['ref_abstract']
        data['group'] = 0
        data['gen_topics'] = []
        data['source'] = 'multi-xscience'
        data['ranking'] = 0
        try:
            res1 = es.index(index="xscience-idx", body=data)
        except Exception as e:
            return {"error": 'Error while inserting data to elasticsearch'}
    else:
        return {"error": 'Invalid Index provided'}

    tfidf_vectorizer = load('tfidf.joblib')
    curr_vec = tfidf_vectorizer.transform([data['title'] + '\n' + data['body']])
    model = load('s_model.joblib')
    group  = int(model.predict(curr_vec)[0])
    try:
        res = es.update(index, id=res1['_id'], body= {

            "doc": {
                "group": int(group)
            }

        })
    except Exception as e:
        return {"Error": 'Error while updating the article group'}

    return {'res': 'Successfully inserted the data'}

'''
API endpoint to search documents based on generated topics
'''
@bp.route('/search')
def search():
    es = Elasticsearch()
    term_list = []

    for token in request.args['q'].split():
        term_list.append({'term': { "gen_topics": token }})
    try:
        res = es.search(index = ['reut-idx', 'jeopardy-idx', 'xscience-idx'], body = {
            "query": {
                "bool" : {
                    "should" : term_list,
                    "minimum_should_match" : 1,
                    "boost" : 1.0
                },
            
            },
            "_source": False,
            "fields": [
                "title",
                "body",
                "source",
                "abstract",
                "summary"
            ]
        })
    except Exception as e:
        return {'Error': 'Error while querying elasticsearch'}

    return {'res': res}


'''
API endpoint to search documents based a query string
'''
@bp.route('/eqsearch')
def string_search():
    print(request.args)
    es = Elasticsearch()
    term_list = []
    q = request.args['q']

    s_res = es.search(index= ['search-idx'], body = {
        "query":{
            "match": {
                "stext": q
            }
        }
    })
    i_res = es.index(index="search-idx", body={
        'stext': request.args['q'], 
        'time': datetime.now()
    })

    try:
        res = es.search(index = ['reut-idx', 'jeopardy-idx', 'xscience-idx'], body = {
            "query": {
                "bool" : {
                    "should" : [
                        { "match": { "body" : q} },
                        { "match": { "abstract" : q }},
                        { "match": { "summary" : q }}
                    ],
                    "minimum_should_match" : 1,
                    "boost" : 1.0
                }
            },
            "_source": False,
            "fields": [
                "title",
                "body",
                "source",
                "abstract",
                "summary"
            ]
        })
    except Exception as e:
        return {'Error': 'Error while querying elasticsearch'}

    return {'res': res, 'psearches': s_res}

'''
API endpoint to improve the classification
'''
@bp.route('/classify')
def classify():
    try:
        classify_docs.load_all()
        classify_docs.classify()
        update_groups.load_groups()
        update_groups.update_groups()
        rank_documents.load_groups()
        rank_documents.gather_docs_by_groups()
    except Exception as e:
        return {'res': 'Error while classifying the docs'}
    return {'res': 'Successfully classified the docs'}