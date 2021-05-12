from elasticsearch import Elasticsearch
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json
from joblib import dump, load

all_docs = []
all_docs_ids = []
all_docs_sources = []
nlp = spacy.load('en_core_web_sm')

'''
Load rueters data from es
'''
def load_ruet():
    es = Elasticsearch()
    res = es.search(index="reut-idx", body={'size' : 5000, "query": {"match_all": {}}})
    for item in res['hits']['hits']:
        all_docs_ids.append(item['_id'])
        out = ''
        out += item['_source']['title'] + '\n'
        out += item['_source']['body']
        all_docs.append(out)
        all_docs_sources.append(item['_source']['source'])

'''
Load rueters data from jeopardy
'''
def load_jeopardy():
    es = Elasticsearch()
    res = es.search(index="jeopardy-idx", body={'size' : 4000, "query": {"match_all": {}}})
    for item in res['hits']['hits']:
        all_docs_ids.append(item['_id'])
        out = ''
        out += item['_source']['summary'] + '\n'
        all_docs.append(out)
        all_docs_sources.append(item['_source']['source'])

'''
Load rueters data from xscience
'''
def load_xscience():
    es = Elasticsearch()
    res = es.search(index="xscience-idx", body={'size' : 3000, "query": {"match_all": {}}})
    for item in res['hits']['hits']:
        all_docs_ids.append(item['_id'])
        out = ''
        out += item['_source']['abstract'] + '\n'
        all_docs.append(out)
        all_docs_sources.append(item['_source']['source'])

def load_all():
    load_ruet()
    load_jeopardy()
    load_xscience()


def spacy_tokenizer(document):
    tokens = nlp(document)
    tokens = [token.lemma_ for token in tokens if (
        token.is_stop == False and \
        token.is_punct == False and \
        token.lemma_.strip()!= '')]
    return tokens

'''
Classifies the documents based on tf-idf similarity using k-means clustering
'''
def classify():
    tfidf_vectorizer = TfidfVectorizer(input = 'content', tokenizer = spacy_tokenizer)
    result = tfidf_vectorizer.fit_transform(all_docs)
    sil = []
    kmax = 50
    for k in range(2, kmax+1):
        kmeans = KMeans(n_clusters = k).fit(result)
        labels = kmeans.labels_
        sil.append(silhouette_score(result, labels, metric = 'euclidean'))
        
    maxpos = sil.index(max(sil))
    n_clusters = maxpos + 2
    model = KMeans(n_clusters=n_clusters, init='k-means++',
               max_iter=300, n_init=100)
    model.fit(result)
    id_to_labels = []
    for idx, doc_id in enumerate(all_docs_ids):
        id_to_labels.append([doc_id, int(model.labels_[idx]), all_docs_sources[idx], all_docs[idx]])
    id_to_labels_dict = {
        'val': id_to_labels
    }
    json_object = json.dumps(id_to_labels_dict, indent = 4)
    with open('id_to_labels.json', 'w') as f:
        f.write(json_object)

    dump(model, 's_model.joblib')


if __name__ == '__main__':
    load_ruet()
    load_jeopardy()
    load_xscience()
    print(len(all_docs_ids))
    classify()
