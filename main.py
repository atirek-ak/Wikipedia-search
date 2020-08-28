# python modules
import os, sys
import xml.sax

# my classes

class WikiDumpHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.title = ""
		self.info_box = ""
		self.body = ""
		self.category = ""
		self.links = ""
		self.references = ""
		self.total_articles = 0
		self.cur_type = ""

	# called automatically by the parser
	def startElement(self,tag,attributes):
		self.cur_type = tag


	# called automatically by parser when content inside 
	# the tag is encountered
	def characters(self,content):
		# content = content.replace("_"," ")
		# if content != "":
		print(content)
		if self.cur_type == "title":
			self.title = content
		elif self.cur_type == "text":
			self.body = content
		elif self.cur_type == "page":
			pass

	# called automatically by the parser
	def endElement(self,tag):
		pass


# arguments
wiki_dump_path = sys.argv[1]
# inverted_index_output_path = sys.argv[2]
# make parser
parser = xml.sax.make_parser()
# turn off namepsaces so that startElement and endElement 
# are called for every tag
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
# change the handler
Handler = WikiDumpHandler()
parser.setContentHandler(Handler)
parser.parse(wiki_dump_path)