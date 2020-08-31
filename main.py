# inbuilt python modules
import os, sys
from os import path
import xml.sax
import re
from collections import defaultdict
from nltk.corpus import stopwords
import Stemmer
import time
# from nltk.stem import SnowballStemmer

# stemmer = SnowballStemmer('english')
stemmer = Stemmer.Stemmer('english')
stopwords = set(stopwords.words('english'))
indexMap = defaultdict(list)
total_articles = 0
wiki_dump_path = str(sys.argv[1])
inverted_output_path = str(sys.argv[2])
stat_file_path = str(sys.argv[3])
dump_tokens = 0

class WikiDumpHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.title = ""
		self.body = ""
		self.cur_type = ""

	# called automatically by the parser
	def startElement(self,tag,attributes):
		global total_articles
		self.cur_type = tag
		if tag == "page":
			total_articles += 1


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
		if tag == "page":
			process_text = ProcessText()
			process_text.first_call(self.title, self.body)
			# global total_articles
			# print(total_articles)
			self.body = ""
			self.title = ""
			self.cur_type = ""

##################################################

class ProcessText:
	def __init__(self):
		self.title = []
		self.body = []
		self.infobox = []
		self.category = []
		self.external_links = []
		self.references = []

	def first_call(self, title, body):
		text = body.split('==References==')
		if len(text) == 1:
			text = body.split('== References == ')
		self.infobox = self.getInfobox(text[0])	
		self.body = self.getBody(text[0])
		self.title = self.getTitle(title)
		if len(text) != 1:
			self.category = self.get_category(text[1])	
			self.external_links = self.get_external_links(text[1])
			self.references = self.get_references(text[1])
		# print(self.title)
		index = Index()
		index.createIndex(self.title, self.body, self.infobox, self.category, self.external_links, self.references)

# process_text calls 
############################
	def tokenize(self, data):
		global dump_tokens
		data = data.encode("ascii", errors="ignore").decode()
		data = re.sub(r'http[^\ ]*\ ', r' ', data) 
		data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data) 
		data = re.sub(r'\—|\%|\$|\'|\||\.|\*|\[|\]|\:|\;|\,|\{|\}|\(|\)|\=|\+|\-|\_|\#|\!|\`|\"|\?|\/|\>|\<|\&|\\|\u2013|\~|\@|\n', r' ', data)
		data = data.lower()
		data = data.split()
		dump_tokens += len(data)
		return data

	def removeStopWords(self, data):
		return [w for w in data if w.lower() not in stopwords and len(w)>1]
		# return data

	def stem(self, data):
		# data = data.lower()
		return stemmer.stemWords(data)

	def getTitle(self, text):
		data = self.tokenize(text)
		data = self.removeStopWords(data)
		data = self.stem(data)
		return data	

# get body
	def getBody(self, text):
		data = re.sub(r'\{\{.*\}\}', r' ', text)
		data = self.tokenize(data)
		data = self.removeStopWords(data)
		data = self.stem(data)
		return data	

# extract info box
	def getInfobox(self, text):
		data = text.split('\n')
		flag = 0
		info = []
		for line in data:
			if re.match(r'\{\{infobox', line):
				flag = 1
				info.append(re.sub(r'\{\{infobox(.*)', r'\1', line))
			elif re.match(r'\{\{Infobox', line):
				flag = 1
				info.append(re.sub(r'\{\{Infobox(.*)', r'\1', line))	
			elif flag == 1:
				if line == '}}':
					flag = 0
					continue
				info.append(line)
		data = self.tokenize(' '.join(info))
		data = self.removeStopWords(data)
		data = self.stem(data)
		return data

	# extract category
	def get_category(self, text):
		data = text.split('\n')
		# print(data)
		categories = []
		for line in data:
			if re.match(r'\[\[Category', line):
				categories.append(re.sub(r'\[\[Category:(.*)\]\]', r'\1', line))
			elif re.match(r'\[\[category', line):
				categories.append(re.sub(r'\[\[category:(.*)\]\]', r'\1', line))	
		data = self.tokenize(' '.join(categories))
		data = self.removeStopWords(data)
		data = self.stem(data)
		return data

	# extract external links
	def get_external_links(self, text):
		data = text.split('\n')
		links = []
		for line in data:
			if re.match(r'\*[\ ]*\[', line):
				links.append(line)
			
		data = self.tokenize(' '.join(links))
		data = self.removeStopWords(data)
		data = self.stem(data)
		return data
	
	# extract references
	def get_references(self, text):
		data = text.split('\n')
		refs = []
		for line in data:
			if re.search(r'<ref', line):
				refs.append(re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line))
		data = self.tokenize(' '.join(refs))
		data = self.removeStopWords(data)
		data = self.stem(data)
		return data
	
#####################

class Index:
	def __init__(self):
		pass

	def createIndex(self, title, body, infobox, category, external_links, references):
		global indexMap
		global total_articles
		words = defaultdict(int)
		d = defaultdict(int)
		for word in title:
			d[word] += 1
			words[word] += 1
		title_index = d
		d = defaultdict(int)
		for word in body:
			d[word] += 1
			words[word] += 1
		body_index = d
		d = defaultdict(int)
		for word in infobox:
			d[word] += 1
			words[word] += 1
		infobox_index = d
		d = defaultdict(int)
		for word in category:
			d[word] += 1
			words[word] += 1
		category_index = d
		d = defaultdict(int)
		for word in external_links:
			d[word] += 1
			words[word] += 1
		external_links_index = d
		d = defaultdict(int)
		for word in references:
			d[word] += 1
			words[word] += 1
		references_index = d
		for word in words.keys():
			t = title_index[word]
			b = body_index[word]
			i = infobox_index[word]
			c = category_index[word]
			l = external_links_index[word]
			r = references_index[word]
			string = 'd' + str(total_articles)
			if t:
				string += 't' + str(t)
			if b:
				string += 'b' + str(b)
			if i:
				string += 'i' + str(i)
			if c:
				string += 'c' + str(c)
			if l:
				string += 'l' + str(l)
			if r:
				string += 'r' + str(r)
			indexMap[word].append(string)


#####################################
class PrintToFile:
	def __init__(self):
		pass

	def output_to_file(self):
		global indexMap
		global inverted_output_path
		if not path.exists(inverted_output_path):
			os.mkdir(inverted_output_path)
		output_file = inverted_output_path + "index.txt"
		with open(output_file,"w") as out:
			for i,word in enumerate(sorted(indexMap.keys())):
				# print(f'{"Word postings written to file: "+str(i+1)}\r', end="")
				postings = indexMap[word]
				# print(str(word)+" "+" ".join(postings))
				out.write(str(word)+" "+" ".join(postings)+"\n")

############################################

class Statfile:
	def __init__(self):
		pass

	def outputToStatfile(self):
		global inverted_output_path
		global stat_file_path
		global dump_tokens
		output_file = inverted_output_path + "index.txt"
		# print(output_file)
		inverted_index_tokens = 0
		file = open(output_file,"r")
		lines = file.readlines() 
		for line in lines:
			inverted_index_tokens += len(line.split(" ")) -1 
		# inverted_index_tokens = len(content.split("\n")) - 1
		file.close()
		file = open(stat_file_path,"w")
		file.write(str(dump_tokens) + "\n")
		file.write(str(inverted_index_tokens) + "\n")
		file.close()
				

# make parser
start = time.time()
parser = xml.sax.make_parser()
# turn off namepsaces so that startElement and endElement 
# are called for every tag
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
# change the handler
Handler = WikiDumpHandler()
parser.setContentHandler(Handler)
parser.parse(wiki_dump_path)
# print to index.txt
print("Time taken = " + str(time.time() - start))
start = time.time()
printObject = PrintToFile()
printObject.output_to_file()
print("Time taken = " + str(time.time() - start))
StatFileObject = Statfile()
StatFileObject.outputToStatfile()
