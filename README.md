# DocumentClassification
Classifying documents and providing search amongst them using Elasticsearch


### Document Classification
1. Data is collected from 3 sources https://github.com/mihaibogdan10/json-reuters-21578, https://www.kaggle.com/tunguz/200000-jeopardy-questions and https://github.com/yaolu/Multi-XScience.
There are approx 12000 documents that are indexed into elastic search
2. This data is then classified into groups. The classification is based on tf-idf similarity using k-means clustering. The optimal nnumber of clusters are determined through the silhouette method
3. The documents within a group are ranked using the LDA algorithm (Latent Dirichlet allocation)


### API endpoints

1. `/api/insert/<index>` - Inserts the data into the specified <index>. The insterted data is assigned a document group.
2. `/api/search?q=some text` - Performs search by generated topics
3. `/api/eqsearch?q=some text` -  Performs normal search to identify the document source
4. `/api/classify` - Improves document classification by re-running the classification task with the newly added data
