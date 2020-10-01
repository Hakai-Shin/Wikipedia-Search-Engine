import timeit
import xml.sax
import os
import sys
import re
import string
import nltk
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords 
nltk.download('stopwords')

docID_cntr = 1
all_tokens_cnt = 0
index_tokens_cnt =0
doc_cntr = 0
docID_title = {}
inverted_index = {}
block = 0
doc_tokens_freq = {}
doc_tokens_cnt = 0
stop_words = set(stopwords.words('english'))


class WikiXmlHandler(xml.sax.handler.ContentHandler):
      def __init__(self):
            self.tag = ""
            self.title_data = ""
            self.text_data = ""
            self.docID = None
      def startElement(self,tag,attribute):
            self.tag = tag
            if(tag=='title'):
              self.title_data = ""
            elif(tag=='text'):
              self.text_data = ""
      def characters(self,data):
            if(self.tag =='title'):
              self.title_data += data
            elif(self.tag == 'text'):
              self.text_data += data
      def endElement(self,tag):
            global docID_cntr,docID_title, doc_tokens_freq, doc_tokens_cnt
            if(self.tag=='title'):
              # fileName = "title/"+ str(self.fileC) + '.txt'
              # with open(fileName,"w+") as f:
              #   #data = re.findall(r"[a-zA-Z]+", self.title_data.lower())        	
              #   #loop(data, self.fileC, 1)
              #   f.write(self.title_data)
              self.docID = docID_cntr
              docID_title[self.docID] = self.title_data
              docID_cntr = docID_cntr + 1
              
            elif(self.tag=='text'):
              #test("text",self.text_data)
              doc = Document(self.title_data, self.text_data, self.docID)
              #print("done parsing doc" + str(self.docID) + "\n")
              doc.processDocument()
              doc_tokens_freq[self.docID] = doc_tokens_cnt
              doc_tokens_cnt = 0
              self.title_data = ""
              self.text_data = ""
      
stemmer = SnowballStemmer('english')        
class Document(object):
        def __init__(self, title, text, docID):
              self.docID = docID
              self.title = title
              self.text = text.lower()
              #self.field_freq = { "T": 0, "I":0, "B": 0, "C": 0, "L": 0, "R": 0}
              self.infobox = None
              self.body = None
              self.category = None
              self.links = None
              self.references = None
              self.table = str.maketrans(dict.fromkeys(string.punctuation))
              
        
        def processDocument(self):
              global doc_cntr,block
              self.processTitle(self.title)
              self.processText(self.text)
              self.processBody(self.body)
              self.processCategory(self.category)
              self.processReferences(self.references)
              if(doc_cntr == 30000):
                 dumpIndex()
                 doc_cntr  = 0
              else:
                 doc_cntr += 1

        
        def processTitle(self, title):
            title = title.lower() 
            title = re.sub(r'[^0-9a-zA-Z]+'," ",title)
            title_tokens = title.split()
            self.preparePosting(title_tokens,"t")
            
        def processText(self, text):
            self.category = re.findall(r"\[\[category:.*\]\]", text)
            self.references = re.findall(r"\{\{cite.*?\}\}", text)
            self.body = text
            #self.infobox = self.findInfoBox(text)
            #test("infobox",self.infobox)

        
        def processLinks(self,text):
            links=[]
            lines = text.split("==external links==")
            if(len(lines)>1):
              lines=lines[1].split("\n")
              for i in range(len(lines)):
                if('* {{' in lines[i] or '{{' in lines[i]):
                  temp=lines[i]
                  temp = re.sub(r'[^0-9a-zA-Z]+'," ",temp) 
                  temp = temp.split()
                  if( "cite" not in temp and "https" not in temp):
                    temp = " ".join(temp)
                    links.append(temp)
            lines = []
            links=' '.join(links)
            if(links != None):
              links_tokens = links.split()
              self.preparePosting(links_tokens,"l")

        def processInfoBox(self,data):
            info = []
            lines = data.split('\n')
            for i in range(len(lines)):
              if('{{infobox' in lines[i]):
                flag=0
                temp=lines[i].split('{{infobox')[1:]
                info.extend(temp)
                while True:
                      if('{{' in lines[i]):
                          count=lines[i].count('{{')
                          flag+=count
                      if('}}' in lines[i]):
                          count=lines[i].count('}}')
                          flag-=count
                      if(flag<=0):
                          break
                      i=i+1
                      if(i>=len(lines)):
                        break
                      temp = lines[i]
                      temp = re.sub(r'[^0-9a-zA-Z]+'," ",temp)
                      temp = re.sub(r'infobox'," ",temp)
                      info.append(temp)
            lines = []
            info = ' '.join(info)
            info = re.sub(r'[^0-9a-zA-Z]+'," ",info)
            if(info != None):
                info_tokens = info.split()
                self.preparePosting(info_tokens,"i")
        
            
                

        def processReferences(self,references_list):
            new_list = ""
            for reference in references_list:
                new_reference = re.sub(r"\{\{cite ", " ", reference)
                new_reference = re.sub(r"\}\}", " ", new_reference)
                #new_reference_list = re.sub(r"\|", "$", new_reference)
                # for item in new_reference_list:
                #   items = item.split("=")
                #   if(len(items)==2):
                #     new_list+=items[1]+" "
                title=re.findall(r"title=[^\|]*",new_reference)
                if(len(title)!=0):
                    title=re.sub(r"title=", " ", title[0])
                    new_list+=title+" "
            new_list = re.sub(r'[^0-9a-zA-Z]+'," ",new_list)           
            #new_list = new_list.translate(self.table)
            #print(new_list)
            reference_tokens = new_list.split()
            self.preparePosting(reference_tokens,"r")
            #test("ref",references_list)
        
        def processCategory(self,category_list):
            new_list = ""
            for category in category_list:
                new_category = re.sub(r"\[\[category:", " ", category)
                new_category = re.sub(r"\]\]", " ", new_category)
                new_list += new_category + " "
            new_list = re.sub(r"-"," ",new_list)
            new_list = re.sub(r'[^0-9a-zA-Z]+'," ",new_list)
            #new_list = new_list.translate(self.table)
            category_tokens = new_list.split()
            self.preparePosting(category_tokens,"c")
            #test("cat",new_list)

        
        def processBody(self, text):
            self.processLinks(text)
            self.processInfoBox(text)
            new_text = re.sub(r"\{\{.*?\}\}", " ", text)
            new_text = re.sub(r"\[\[file:.*?\]\]", " ", new_text)
            #new_text = re.sub(r"={2,3} ?", "", new_text)
            new_text = re.sub(r"[-'|=*]", " ", new_text)
            new_text = re.sub(r"((http[s]?:\/\/)|(www\.))(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"," ",new_text)
            #new_text = re.sub(r"[.,|+-@~`:;?()*\"=\\&/<>[](){}#!%^$]" , " ", new_text)
            new_text = re.sub(r"\[\[category:.*\]\]"," ",new_text)
            new_text = re.sub(r"\<.*?\>", " ", new_text)
            #new_text = re.sub(r"[*=]", " ", new_text)
            new_text = re.sub(r'[^0-9a-zA-Z]+'," ",new_text)
            #new_text = new_text.translate(self.table)
            #new_text = stemmer.stem(new_text)
            body_tokens = new_text.split()
            self.preparePosting(body_tokens,"b")
            #test("text",text)
            #test("newtext",new_text)
        
        def preparePosting(self,tokens,tag):
          global stop_words, inverted_index, all_tokens_cnt, doc_tokens_cnt
          docID = self.docID
          all_tokens_cnt += len(tokens)
          for token in tokens:
                if(validateToken(token)):
                    doc_tokens_cnt = doc_tokens_cnt + 1 
                    token = stemmer.stem(token)
                    if(token in inverted_index):  #if term present in inverted index
                        posting_list = inverted_index[token]
                        if(self.docID in posting_list):  # term is present but posting list corresponding to docid not present
                            if(tag in posting_list[docID]):
                               posting_list[docID][tag] = posting_list[docID][tag] + 1
                            else:
                               posting_list[docID][tag] = 1
                            #posting_list[docID]['f'] += 1
                        else:
                            posting ={}
                            #posting['f']=1
                            #posting={'f':1,'t':0,'i':0,'b':0,'c':0,'l':0,'r':0}
                            posting[tag] = 1
                            posting_list[docID] = posting
                    else:
                        posting={}
                        #posting['f']=1
                        #posting={'f':1,'t':0,'i':0,'b':0,'c':0,'l':0,'r':0}
                        posting_list={}
                        posting[tag] = 1
                        posting_list[docID] = posting
                        inverted_index[token] = posting_list

def checkalnum(s):
    letter_flag = False
    number_flag = False
    for i in s:
        if i.isalpha():
            letter_flag = True
        if i.isdigit():
            number_flag = True
    return letter_flag and number_flag

def validateToken(token):
    if(token in stop_words): #token is a stopword
        return False
    if(checkalnum(token)): #token is alphanumeric
        return False
    if(len(token)>20):
        return False
    if(len(token)==1):
        return False
    if(token.isnumeric()):
        if(len(token)>6):
          return False
    return True

def gendocidTitleFile():
    global docID_title,doc_tokens_freq
    docidlist = sorted(list(docID_title.keys()))
    with open("docid_title.txt", "w+") as f:
          for docid in docidlist:
             id_title_str=":".join((str(docid),str(doc_tokens_freq[docid]),docID_title[docid]))
             f.write(id_title_str + "\n")
    f.close()
    docID_title = dict()

def genDocCnt():
    global docID_cntr
    with open("doc_cnt.txt", "w+") as f:
          f.write(str(docID_cntr - 1))
    f.close()




def dumpIndex():
      global inverted_index, block, index_tokens_cnt
      print("Started creating index block " + str(block))
      index_loc = "index_blocks"
      fileName = "".join((index_loc,"/inverted_index",str(block),".txt"))
      with open(fileName,"w+") as f:
          terms = sorted(inverted_index.keys())
          index_tokens_cnt = len(terms)
          #i=1
          for term in terms:
            posting_string = ""
            for docID,posting in inverted_index[term].items():
              #posting =  inverted_index[term][docID]
              doc_string = ''.join('{}{}'.format(key,value) for key, value in posting.items())
              doc_string = "".join((str(docID),doc_string  ))
              #doc_string = "".join(("|$d:",str(docID),"|f:",str(posting['freq']),"|t:",str(posting['t']),"|i:",str(posting['i']),"|b:",str(posting['b']),"|c:",str(posting['c']),"|l:",str(posting['l']),"|r:",str(posting['r']),"$"  )
              # doc_string  = "$d:" + str(docID) + "|f:" + str(posting['freq']) 
              # doc_string += "|t:" + str(posting['t']) + "|i:" + str(posting['i']) 
              # doc_string += "|b:" + str(posting['b']) + "|c:" + str(posting['c']) 
              # doc_string += "|l:" + str(posting['l']) + "|r:" + str(posting['r']) + "$"
              posting_string = "".join((posting_string,doc_string,"|"))
            posting_string = ":".join((term,posting_string))
            f.write(posting_string + "\n")
            #print(i)
            #i=i+1
          inverted_index.clear()
      print("created index block " + str(block) + "\n")
      block = block + 1
      f.close()


def dumpCharPosting(charIndex,folder):
    index_keys = charIndex.keys()
    for temp_char in index_keys:
        fileName = "".join((folder,"/",temp_char,".txt"))
        with open(fileName,"a+") as f:
          char_posting_list = charIndex[ temp_char ]
          for posting_string in char_posting_list:
              f.write(posting_string)
        f.close()


def charWiseIndex(folder):
    comm ="".join(("rm -rf ",folder,"; mkdir ",folder))
    os.system(comm)
    char_posting = dict()
    arr = os.listdir("index_blocks")
    print(arr)
    for file_name in arr:
      if(file_name != ".ipynb_checkpoints"):
        print("creating character wise index files for " + file_name + "\n")
        index_file = "/".join(("index_blocks",file_name))
        with open(index_file,"r") as f:
              index_dump=f.readlines()
        f.close()
        for index_string in index_dump:
            index_tokens = index_string.split(":")
            #print(index_tokens[0],file_name)
            term_char = index_tokens[0][0]
            if( term_char.isalpha()):
                  if(term_char in char_posting.keys()):
                      char_posting[term_char].append(index_string)
                  else:
                      char_posting[term_char] = list()
                      char_posting[term_char].append(index_string)
            else:
                  if('special' in char_posting.keys()):
                      char_posting['special'].append(index_string)
                  else:
                      char_posting['special'] = list()
                      char_posting['special'].append(index_string)                    
        dumpCharPosting(char_posting,folder)
        print("Character wise index files created for " + file_name + "\n")
        char_posting = dict()                      
            
def dumpTermPosting(termIndex,filename):
    sorted_file = filename
    #sorted_file = "".join(("sorted","/",filename))
    index_keys = sorted(list(termIndex.keys()))
    with open(sorted_file,"w+") as f:
        for term in index_keys:    
          posting_list = termIndex[ term ]
          posting_string = "".join(posting_list)
          posting_string = ":".join((term,posting_string))
          posting_string = re.sub("\n", "", posting_string)
          f.write(posting_string + "\n")
    f.close()


def sortCharBlock(folder):
    term_posting = dict()
    arr = os.listdir(folder)
    for file_name in arr:
      if(file_name != ".ipynb_checkpoints"):
        print("Sorting " + file_name + "\n")
        index_file = "/".join((folder,file_name))
        with open(index_file,"r") as f:
              index_dump=f.readlines()
        f.close()
        for index_string in index_dump:
            index_tokens = index_string.split(":")
            term = index_tokens[0]
            if(term in term_posting.keys()):
              term_posting[term].append(index_tokens[1])
            else:
              term_posting[term] = list()
              term_posting[term].append(index_tokens[1])                   
        dumpTermPosting(term_posting,index_file)
        print(file_name + " Sorted.\n")
        term_posting = dict()

def test(tag,values):
    print(len(values))
    fileName = tag + '.txt'
    with open(fileName,"w+") as f:
              for item in values:
                f.write(item)
    f.close()

def main():

    parser = xml.sax.make_parser()                                  #SAX Parser
    handler = WikiXmlHandler()                                         # Object for handling xml
    parser.setContentHandler(handler)
    data_folder = sys.argv[1]
    arr = os.listdir(data_folder)
    i=1
    for file_name in arr:
      if(file_name != ".ipynb_checkpoints"):
        file_name = "/".join((data_folder,file_name))
        print("{1}. Started parsing {0}".format(file_name,i))
        parser.parse(file_name)
        print("Done parsing")
        i=i+1
    dumpIndex()
    with open("inverted_index_stats.txt","w+") as f:
        f.write(str(all_tokens_cnt)+"\n"+str(index_tokens_cnt))
    f.close()
    index_files_loc = sys.argv[2]
    charWiseIndex(index_files_loc)
    sortCharBlock(index_files_loc)
    gendocidTitleFile()
    genDocCnt()
    os.system("rm -rf index_blocks")



if __name__ == "__main__":                                            #main
    start = timeit.default_timer()
    os.system("mkdir index_blocks")
    main()
    stop = timeit.default_timer()
    print(stop - start)
