import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import numpy as np
from elasticsearch import Elasticsearch

groups_dict = {}

'''
Load the documents into groups_dict based on the group number
'''
def load_groups():
    with open('id_to_labels.json') as f:
        data = json.load(f)['val']
        for item in data:
            if(groups_dict.get(item[1], 0) == 0):
                groups_dict[item[1]] = [(item[0], item[2], item[3])]
            else:
                groups_dict[item[1]].append((item[0], item[2], item[3]))

'''
Returns the ranking of the documents in a group
'''
def gen_topics(H, W, feature_names, documents, no_top_words, no_top_documents):
    for topic_idx, topic in enumerate(H):
        topic_words = [feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]
        top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_documents]
        docs_ordering = []
        for doc_index in top_doc_indices:
            docs_ordering.append(doc_index)
    
    return (docs_ordering, topic_words)

'''
Applies LDA to the documents for topic modelling
'''
def rank_docs(documents, no_docs):
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    tf = tf_vectorizer.fit_transform(documents)
    tf_feature_names = tf_vectorizer.get_feature_names()
    lda_model = LatentDirichletAllocation(n_components=1, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
    lda_W = lda_model.transform(tf)
    lda_H = lda_model.components_
    return gen_topics(lda_H, lda_W, tf_feature_names, documents, 5, no_docs)

'''
Updates the rank of the documents in elasticsearch
'''
def gather_docs_by_groups():
    for k, v in groups_dict.items():
        j = 0
        r = 0
        docs_list = []
        docs_index_list = []
        docs_id_list = []
        for item in v:
            j += 1
            index = ''
            if(item[1] == 'reut2'):
                index = "reut-idx"
            elif item[1] == 'jeopardy':
                index = "jeopardy-idx"
            else:
                index = "xscience-idx"
            docs_list.append(item[2])
            docs_index_list.append(index)
            docs_id_list.append(item[0])
        docs_ordering, topic_words = rank_docs(docs_list, j)
        print(topic_words)
        for idx in docs_ordering:
            r += 1
            update_doc_ranks(docs_id_list[idx], docs_index_list[idx], r, topic_words)

def update_doc_ranks(doc_id, index, rank, topic_words):
    es = Elasticsearch()
    print(doc_id, index, rank)
    res = es.update(index, id=doc_id, body= {
        'doc': {
            'ranking': int(rank),
            'gen_topics': topic_words
        }
    })
    print(res)

            
if __name__ == '__main__':
    load_groups()
    gather_docs_by_groups()



