import sys
import re
import math
import timeit

overall_num_docs = 0
results = []
docid2title = {}

from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer('english') 

def getOverallDocCnt():
    global overall_num_docs
    with open("doc_cnt.txt", "r") as f:
          cnt = f.readline()
          overall_num_docs = int(cnt)
    f.close()


def processQuery(query,index_file_loc):
    i=0
    k=""
    while(query[i]!=","):
        k=k+query[i]
        i=i+1
    query = query[i+2:]
    #print(query,k)
    if(re.search(r'[b|c|l|i|r|t]:',query)):  # body category externalLinks infobox reference title
      print("Field query. \n")
      field_query(query,index_file_loc,k)
    else:
      print("Simple query. \n")
      simple_query(query,index_file_loc,k)

def getTF(field_freq):
    weightedFreq = 0
    for field in field_freq.keys():
      if(field == "t"):
        weightedFreq = weightedFreq + field_freq[field] * 0.3
      elif(field == "b"):
        weightedFreq = weightedFreq + field_freq[field] * 0.25
      elif(field == "c"):
        weightedFreq = weightedFreq + field_freq[field] * 0.05
      elif(field == "r"):
        weightedFreq = weightedFreq + field_freq[field] * 0.1
      elif(field == "l"):
        weightedFreq = weightedFreq + field_freq[field] * 0.05
      elif(field == "i"):
        weightedFreq = weightedFreq + field_freq[field] * 0.25
    return 1.0 + math.log10(1.0 + weightedFreq)

def getTfidfScore(termFreq,num_docs):
     global overall_num_docs
     idf = math.log10(float(overall_num_docs)/num_docs)
     tf = getTF(termFreq)
     tfidf = tf * idf
     return tfidf

def prepdocidtitle():
    global docid2title
    with open("docid_title.txt", "r") as f:
        doctitlelist = f.readlines()
    f.close()
    for docid_title in doctitlelist:
            docid_title =docid_title.replace(':', '?', 2)
            docid_title = docid_title.split("?")
            docid = docid_title[0]
            doctitle = docid_title[2]
            docid2title[docid] =doctitle

    

def rankDocuments(documents,k):
      global results
      tf_idf = dict()
      k=int(k)
      #for docid in documents.keys():
      #      tf = getTF(documents[docid])
      #      tfidf = tf * idf
      #      tf_idf[docid] = tfidf
      if(k>len(documents)):
        k=len(documents)
      #print(len(documents))
      #print(k)
      tf_idf = sorted(documents.items(), key=lambda x:x[1], reverse=True)[:k]
      #print(len(tf_idf))
      for doctuple in tf_idf:
          docid = doctuple[0]
          if(docid in docid2title.keys()):
              title = docid2title[docid]
              title =title.lower()
              title = re.sub("\n", "", title)
              print("{0}, {1}".format(docid,title))
              output = ", ".join((docid,title))
              results.append(output)
            


def field_query(query,folder,k): # t:World Cup, i:2019, c:Cricket
    query = query.split(",") # ["t:World Cup" "i:2019" "c:Cricket"]
    documents =dict()
    for subquery in query:  # t:World Cup
      query_field = []
      query_field.append(subquery[0]) #[t]
      subquery = subquery[2:]         # World Cup
      subquery = subquery.split()  # [ World, Cup]
      for term in subquery: # World
        term = stemmer.stem(term)
        termChar = term[0]  # W
        if(termChar.isalpha()==False):
            termChar = "special"
        index_file_name = "/".join((folder,termChar + ".txt"))
        with open(index_file_name, "r") as f:
              posting_string = f.readline()
              posting_string = re.sub("\n", "", posting_string) # term:docidi1|docidt1|
              while(len(posting_string)!=0):
                  posting_arr = posting_string.split(":") # [term docidf1i1|docidt1|]
                  if(posting_arr[0] == term):
                      #with open("test1.txt", "w+") as tt:
                      #  tt.write(posting_string)
                      #f.close()
                      posting_list = posting_arr[1].split("|") # [ docidf1i1 docidf1t1]
                      posting_list = [tokenizePosting(posting) for posting in posting_list] # [ [docid,i,1],[docid,t,1]]
                      num_docs = len(posting_list)
                      for posting in posting_list: # [docid,i,1]
                          docid = posting[0]
                          term_freq = getFreq(posting,query_field) #[i:1] [t] == # {t:0,i:0,b:0,c:0,l:0,r:0}
                          tfidf = getTfidfScore(term_freq,num_docs)
                          if(docid in documents.keys()):
                              documents[docid] = documents[docid] + tfidf
                          else:
                            documents[docid] = tfidf
                          #if(docid in documents.keys()): 
                          #    for field in term_freq.keys():   
                          #        documents[docid][field] = documents[docid][field] + term_freq[field]
                          #else:
                          #    documents[docid] = term_freq
                      break
                  else:
                      posting_string = f.readline()
                      posting_string = re.sub("\n", "", posting_string)
        f.close()
    rankDocuments(documents,k)

def tokenizePosting(posting): # 7085065f1b2
    postlist = []
    digits = ""
    for i in range(0,len(posting)):
        if(posting[i].isalpha()):
            postlist.append(digits)
            digits=""
            postlist.append(posting[i])
        else:
            digits="".join((digits,posting[i]))
    postlist.append(digits)
    return postlist



                                   #  0     1 2 3 4
def getFreq(posting,query_fields): # [docid,i,1,b,2]  [t,b,c,l,r,i] / [ t  ]
    i=1
    term_freq = {"t":0,"b":0,"c":0,"l":0,"r":0,"i":0}
    while(i<len(posting)):    # i<5
      if(posting[i] in query_fields):
          term_freq[posting[i]] = int(posting[i+1])
      i=i+2 #1 3 5*
    return term_freq  # [t:0,i:1,b:2,c:0,l:0,r:0]


def simple_query(query,folder,k):
    query_field = ["t","b","c","l","r","i"]
    query = query.split()
    #print(query)
    documents =dict()
    for term in query:
      term = stemmer.stem(term)
      termChar = term[0]
      if(termChar.isalpha()==False):
          termChar = "special"
      index_file_name = "/".join((folder,termChar + ".txt"))
      with open(index_file_name, "r") as f:
            posting_string = f.readline()
            posting_string = re.sub("\n", "", posting_string) # term:docidi1|docidt1|
            while(len(posting_string)!=0):
                posting_arr = posting_string.split(":") # [term docidf1i1|docidt1|]
                if(posting_arr[0] == term):
                      """ with open("test1.txt", "w+") as tt:
                        tt.write(posting_string)
                      f.close()"""
                      posting_list = posting_arr[1].split("|") # [ docidf1i1 docidf1t1]
                      posting_list = [tokenizePosting(posting) for posting in posting_list] # [ [docid,i,1],[docid,t,1]]
                      num_docs = len(posting_list)
                      for posting in posting_list: # [docid,i,1]
                          docid = posting[0]
                          term_freq = getFreq(posting,query_field) #[i:1] [t] == # {t:0,i:0,b:0,c:0,l:0,r:0}
                          tfidf = getTfidfScore(term_freq,num_docs)
                          if(docid in documents.keys()):
                              documents[docid] = documents[docid] + tfidf
                          else:
                            documents[docid] = tfidf
                          #if(docid in documents.keys()): 
                          #    for field in term_freq.keys():   
                          #        documents[docid][field] = documents[docid][field] + term_freq[field]
                          #else:
                          #    documents[docid] = term_freq
                      break
                else:
                      posting_string = f.readline()
                      posting_string = re.sub("\n", "", posting_string)
      f.close()
    rankDocuments(documents,k)




def main():
    global results
    start = timeit.default_timer()
    getOverallDocCnt()
    prepdocidtitle()
    with open("2019201054_queries_op.txt", "w+") as f:
        index_file_loc = sys.argv[1]
        query_file = sys.argv[2]
        with open(query_file, "r") as q:
            queries = q.readlines()
        q.close()
        if(queries[0].isnumeric()):
          num_lines = int(queries[0])+1
          print("Number of queries given explicitly. \n")
          i=1
        else:
          num_lines = len(queries)
          print("Number of queries given implicitly. \n")
          i=0
        while(i<num_lines):
            query = queries[i]
            start = timeit.default_timer()
            query = query.lower()
            query = re.sub("\n", "", query)
            print(query)
            processQuery(query,index_file_loc)
            stop = timeit.default_timer()
            time_taken = stop - start
            for output in results:
                  f.write(output + "\n")
            f.write(str(time_taken) + "\n" +"\n")
            i = i + 1
            results =[]
            print("Time taken:"+str(stop-start)+"\n")
            start = timeit.default_timer()
    f.close()

    



if __name__ == "__main__":    
    main()