# Wikipedia Search Engine

## About

There are two parts in this search engine, indexing and searching. 

### Indexing

In Indexing part, Each article in the dump is assigned a document id. Then we are processing the sections in each article, these sections are: Title, Body, Infobox, Category, References, External Links. For text present in each section, we are tokenization the text, stemming each token(term) to its root word. for each term we prepare a posting which contains the document id  of the document containing this term, frequency of this term in each section. This posting is stored in a posting list and we have a posting list for each unique term. Finally we store each term along with its posting list in files based on the first character of the term, our inverted index contains 26(alphabets) + 1(special character and numbers) = 27 files.
Hence, a dump containing 43 GB data is reduced to inverted_index files which form a total of 11 GB size, which is effectively 25% of the original dump size.

### Searching

In Searching, We give queries to the system. Each query can either be simple query like " Lord of the rings " or a field query like " t:Lord of the rings b:Mount Doom" which means in the result document, the title must contain words Lord of the rings and body must contain words mount doom. each query is tokenized, each token is stemmed. We get the posting list for each term in query. For each document in the posting list, we find Term_Frequency_Inverse_Document_Frequency score for each document corresponding to that query term and for each query terms we sum up the TFIDF score for documents common among query terms, this will give list of documents , along with their TFIDF scores, which contains the given query terms. We then sort this list on the tfidf score and return the document titles with high tfidf scores. 
Hence, using tfidf for relevance ranking, we get the most relevant document title for given query.

## Data files

The Dump is a group of xml files containing wikipedia articles. This dump data can be found online.


## To run

To run the system, ```cd``` into Wikipedia_search_Engine repository and run the following commands.

```
source wikipedia_search_engine-venv/bin/activate
cd src

```
Place the folder containing 43 GB Dump data in src folder, then run the following commands one by one.

```

python3 wiki_indexer.py <argument_1> <argument_2>
python3 wiki_search.py <argument2> queries.txt

```

argument_1 : folder name containing 43 GB wiki dump
arguement_2 : folder where inverted index files will be stored and used during searching

### Example:

```

python3 wiki_indexer.py dump inverted_index
python3 wiki_search.py inverted_index queries.txt

```

### Output:

#### wiki_index.py

* Folder containing inverted_index files

* inverted_index_stats.txt, file containing total number of terms in complete dump and total number of terms in inverted_index 

* doc_cnt.txt, file containing total number of documents(articles) in the dump

* docid_title.txt, file containing (document id, number of terms in a document, document title) for each document in the dump

#### wiki_search.py

* search_results.txt, file containing search results (document id and document title) and time taken to execute for each query present in queries.txt file




