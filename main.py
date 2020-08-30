# inbuilt python modules
import os, sys
import xml.sax

# my classes
import inverseIndex as my_tokenizer

class WikiDumpHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.title = ""
		self.body = ""
		self.total_articles = 0
		self.cur_type = ""
		self.arg_list = []

	# called automatically by the parser
	def startElement(self,tag,attributes):
		self.cur_type = tag
		if tag == "page":
			self.total_articles += 1


	# called automatically by parser when content inside 
	# the tag is encountered
	def characters(self,content):
		# print(content, end='')
		if self.cur_type == "title":
			self.title += content
		elif self.cur_type == "text":
			self.body += content

	# called automatically by the parser
	def endElement(self,tag):
		# print(self.body)
		if tag == "title":
			self.arg_list.append(self.title)
		elif tag == "text":
			self.arg_list.append(self.body)
		elif tag == "page":
			self.body = ""
			self.title = ""
			self.cur_type = ""
			# call tokenizer
			my_tokenizer.process_text(self.total_articles, self.arg_list, inverted_output)
			self.arg_list = []

# arguments
wiki_dump_path = sys.argv[1]
inverted_output = sys.argv[2]
# make parser
parser = xml.sax.make_parser()
# turn off namepsaces so that startElement and endElement 
# are called for every tag
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
# change the handler
Handler = WikiDumpHandler()
parser.setContentHandler(Handler)
parser.parse(wiki_dump_path)