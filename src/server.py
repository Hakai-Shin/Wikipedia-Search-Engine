import timeit
import xml.sax
import os


class WikiXmlHandler(xml.sax.handler.ContentHandler):
      def __init__(self):
            self.tag = ""
            self.title_data = ""
            self.text_data = ""
            self.fileC = 1
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
            if(self.tag=='title'):
              fileName = "title/"+ str(self.fileC) + '.txt'
              with open(fileName,"w+") as f:
                #data = re.findall(r"[a-zA-Z]+", self.title_data.lower())        	
                #loop(data, self.fileC, 1)
                f.write(self.title_data)
            elif(self.tag=='text'):
              fileName = "text/"+ str(self.fileC) + '.txt'
              with open(fileName,"w+") as f:
                #process(self.text_data.lower(), self.fileC)
                self.fileC += 1
                f.write(self.text_data)
            if(self.fileC>50):
              return

def main():
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