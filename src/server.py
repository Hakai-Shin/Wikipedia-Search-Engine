import timeit
import xml.sax
import os
import re
import string
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords 

docID_cntr = 1
title_docID = {}
inverted_index = {}
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
            global docID_cntr
            if(self.tag=='title'):
              # fileName = "title/"+ str(self.fileC) + '.txt'
              # with open(fileName,"w+") as f:
              #   #data = re.findall(r"[a-zA-Z]+", self.title_data.lower())        	
              #   #loop(data, self.fileC, 1)
              #   f.write(self.title_data)
              title_docID[self.title_data] = docID_cntr
              self.docID = docID_cntr
              docID_cntr = docID_cntr + 1
              
            elif(self.tag=='text'):
              test("text",self.text_data)
              doc = Document(self.title_data, self.text_data, self.docID)
              doc.processDocument()
              self.title_data = ""
              self.text_data = ""
      
stemmer = PorterStemmer()        
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
              self.processTitle(self.title)
              self.processText(self.text)
              # self.processInfoBox(self.infobox, self.docID)
              self.processBody(self.body)
              self.processCategory(self.category)
              # self.processLinks(self.links, self.docID)
              self.processReferences(self.references)

        
        def processTitle(self, title):
            title = title.lower() 
            title = re.sub(r'[^0-9a-zA-Z]+'," ",title)
            title_tokens = title.split()
            self.preparePosting(title_tokens,"t")
            
        def processText(self, text):
            self.category = re.findall(r"\[\[category:.*\]\]", text)
            self.references = re.findall(r"\{\{cite.*?\}\}", text)
            self.body = text
            #test("infobox",self.infobox)
        
        def processReferences(self,references_list):
            new_list = ""
            for reference in references_list:
                new_reference = re.sub(r"\{\{cite ", "", reference)
                new_reference = re.sub(r"\}\}", " ", new_reference)
                #new_reference_list = re.sub(r"\|", "$", new_reference)
                # for item in new_reference_list:
                #   items = item.split("=")
                #   if(len(items)==2):
                #     new_list+=items[1]+" "
                title=re.findall("title=[^\|]*",new_reference)[0]
                title=re.sub(r"title=", "", title)
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
                new_category = re.sub(r"\[\[category:", "", category)
                new_category = re.sub(r"\]\]", " ", new_category)
                new_list += new_category + " "
            new_list = re.sub(r"-"," ",new_list)
            new_list = new_list.translate(self.table)
            category_tokens = new_list.split()
            self.preparePosting(category_tokens,"c")
            #test("cat",new_list)

        
        def processBody(self, text):
            new_text = re.sub(r"\{\{.*?\}\}", "", text)
            new_text = re.sub(r"\[\[file:.*?\]\]", "", new_text)
            new_text = re.sub(r"={2,3} ?", "", new_text)
            new_text = re.sub(r"[-'|]", " ", new_text)
            new_text = re.sub("((http[s]?:\/\/)|(www\.))(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+","",new_text)
            #new_text = re.sub(r"[.,|+-@~`:;?()*\"=\\&/<>[](){}#!%^$]" , " ", new_text)
            new_text = re.sub(r"\[\[category:.*\]\]","",new_text)
            new_text = re.sub(r"\<.*?\>", "", new_text)
            new_text = re.sub(r"[*=]", " ", new_text)
            new_text = new_text.translate(self.table)
            #new_text = stemmer.stem(new_text)
            body_tokens = new_text.split()
            self.preparePosting(body_tokens,"b")
            #test("text",text)
            #test("newtext",new_text)
        
        def preparePosting(self,tokens,case):
          global termID_cntr, stop_words, inverted_index
          for token in tokens:
                if(token not in stop_words): 
                    token = stemmer.stem(token)
                    if(token in inverted_index.keys()):  #if term present in inverted index
                        posting_list = inverted_index[token]
                        if(self.docID in posting_list.keys()):  # term is present but posting list corresponding to docid not present
                            posting_list[docID][tag] += 1
                            posting_list[docID]['freq'] += 1
                        else:
                            posting={'freq':1,'t':0,'i':0,'b':0,'c':0,'l':0,'r':0}
                            posting[tag] += 1
                            posting_list[docID] = posting
                    else:
                        posting={'freq':1,'t':0,'i':0,'b':0,'c':0,'l':0,'r':0}
                        posting_list={}
                        posting[tag] += 1
                        posting_list[docID] = posting
                        inverted_index[term] = posting_list
                      
                      
            


def test(tag,values):
    print(len(values))
    fileName = tag + '.txt'
    with open(fileName,"w+") as f:
              for item in values:
                f.write(item)

def main():
    global termID_cntr, docID_cntr, term_termID, title_docID
    parser = xml.sax.make_parser()                                  #SAX Parser
    handler = WikiXmlHandler()                                         # Object for handling xml
    parser.setContentHandler(handler)
    file = "data/ex.xml"
    parser.parse(file)

if __name__ == "__main__":                                            #main
    start = timeit.default_timer()
    os.system("rm -rf title; mkdir title")
    os.system("rm -rf text; mkdir text")
    main()
    stop = timeit.default_timer()
    print(stop - start)