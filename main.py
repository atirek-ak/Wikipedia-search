import heapq
import os, sys
from os import path
import xml.sax
import re
from collections import defaultdict
from nltk.corpus import stopwords
import Stemmer
import time

total_documents = 99 # stores number of files inverted index is divided into
total_titles = 1 # total title file
titles_map = defaultdict(list)
document_terms = [] # stores number of terms in a document
indexMap = defaultdict(list)
article_number = 0 #stores total number of articles in the end
# modules  
stemmer = Stemmer.Stemmer('english')
stopwords = set(stopwords.words('english'))
# args
wiki_dump_path = str(sys.argv[1])
inverted_output_path = str(sys.argv[2])

class WikiDumpHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.title = ""
		self.body = ""
		self.cur_type = ""

	# called automatically by the parser
	def startElement(self,tag,attributes):
		self.cur_type = tag
			

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
			global titles_map
			global article_number
			article_number += 1
			titles_map[article_number].append(self.refine(self.title))
			process_text = ProcessText()
			process_text.first_call(self.title, self.body)
			self.body = ""
			self.title = ""
			self.cur_type = ""

	def refine(self, title):
		return title.strip().lower()

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
		# words in the document after tokenization, stop word removal and stemming	
		global document_terms
		total_words = len(self.infobox) + len(self.body) + len(self.title) + len(self.category) + len(self.external_links) + len(self.references)
		document_terms.append(total_words)
		# create index
		index = Index()
		index.createIndex(self.title, self.body, self.infobox, self.category, self.external_links, self.references)

# process_text calls 
############################
	def tokenize(self, data):
		data = data.encode("ascii", errors="ignore").decode()
		data = re.sub(r'http[^\ ]*\ ', r' ', data) 
		data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data) 
		data = re.sub(r'\—|\%|\$|\'|\||\.|\*|\[|\]|\:|\;|\,|\{|\}|\(|\)|\=|\+|\-|\_|\#|\!|\`|\"|\?|\/|\>|\<|\&|\\|\u2013|\~|\@|\n', r' ', data)
		data = data.lower()
		# data = data.split()
		return data.split()

	def removeStopWords(self, data):
		return [w for w in data if w.lower() not in stopwords and len(w)>1]
		# return data

	def stem(self, data):
		# data = data.lower()
		return stemmer.stemWords(data)

# get body
	def getBody(self, text):
		data = re.sub(r'\{\{.*\}\}', r' ', text)
		data = self.tokenize(data)
		data = self.removeStopWords(data)
		data = self.stem(data)
		return data	

	def getTitle(self, text):
		data = self.tokenize(text)
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
		global article_number
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
			string = 'd' + str(article_number)
			t = title_index[word]
			if t:
				string += 't' + str(t)
			b = body_index[word]
			if b:
				string += 'b' + str(b)
			i = infobox_index[word]
			if i:
				string += 'i' + str(i)
			c = category_index[word]
			if c:
				string += 'c' + str(c)
			l = external_links_index[word]
			if l:
				string += 'l' + str(l)
			r = references_index[word]
			if r:
				string += 'r' + str(r)
			indexMap[word].append(string)
		# print(article_number%20000==0)	
		if article_number%100000 == 0:
			printIndex = PrintToFile()
			printIndex.output_to_file()
			print("1L done")

		if article_number%100000 == 0:	
			TitleObject = TitlesFile()
			TitleObject.output_to_file()
			print("1L titles done")

#####################################
class PrintToFile:
	def __init__(self):
		pass

	def output_to_file(self):
		global indexMap
		global inverted_output_path
		global total_documents
		total_documents += 1
		if not path.exists(inverted_output_path):
			os.mkdir(inverted_output_path)
		output_file = inverted_output_path + "index" + str(total_documents)+".txt"
		with open(output_file,"w") as out:
			for i,word in enumerate(sorted(indexMap.keys())):
				# print(f'{"Word postings written to file: "+str(i+1)}\r', end="")
				postings = indexMap[word]
				# print(str(word)+" "+" ".join(postings))
				out.write(str(word)+" "+" ".join(postings)+"\n")
		# clear global variables for next iteration
		indexMap = defaultdict(list)

############################################
# also prints number of terms of document in the dam file 
class TitlesFile:
	def __init__(self):
		pass

	def output_to_file(self):
		global titles_map
		global document_terms
		global total_titles
		output_path = "./title/"
		if not path.exists(output_path):
			os.mkdir(output_path)
		output_file = output_path + "title" + str(total_titles) + ".txt"
		with open(output_file,"w") as out:
			for i,index in enumerate(titles_map):
				title = titles_map[index]
				out.write(str(index) + " " + str(title[0]) + ":" + str(document_terms[i]) + "\n")
		document_terms = []
		titles_map = defaultdict(list)	
		total_titles += 1			

############################################

class Merge:
	def __init__(self):
		global total_documents
		self.cur_file = 1
		self.total_documents = total_documents
		self.input_path = "./index/"
		self.output_path = "./Inverted Index/"
		self.files = {}
		self.flag = [0] * total_documents
		self.top = {}
		self.heap = []
		self.words = {}
		self.count = 0
		self.data = defaultdict(list)

	def mergeFiles(self):
		if not path.exists(self.output_path):
			os.mkdir(self.output_path)
		for i in range(self.total_documents):
			filename = "./index/index" + str(i+1) + ".txt"
			self.files[i] = open(filename,"r")
			self.flag[i] = 1
			self.top[i] = self.files[i].readline().strip()
			self.words[i] = self.top[i].split()
			# print(self.words[i][0])
			if self.words[i][0] not in self.heap:
				heapq.heappush(self.heap, self.words[i][0])
		
		while any(self.flag) == 1:
			self.count += 1
			temp = heapq.heappop(self.heap)
			for i in range(self.total_documents):
				if self.flag[i]:
					if self.words[i][0] == temp:
						self.data[temp].extend(self.words[i][1:])
						self.top[i] = self.files[i].readline().strip()
						if self.top[i] == '':
							self.flag[i] = 0
							self.files[i].close()
						else:
							self.words[i] = self.top[i].split()
							if self.words[i][0] not in self.heap:
								heapq.heappush(self.heap, self.words[i][0])
			
			if self.count % 500000 == 0:
				self.output_to_file()
				print(str(self.count) + " done")
		# print remaining		
		self.output_to_file()
		print("remaining done")		

	def output_to_file(self):
		filename = self.output_path + str(self.cur_file) + ".txt"
		with open(filename,"w") as out:
			for i,word in enumerate(sorted(self.data.keys())):
				out.write(str(word)+" "+" ".join(self.data[word])+"\n")
		
		self.data = defaultdict(list)
		self.cur_file += 1	
############################################
				

# make parser
# start = time.time()
# parser = xml.sax.make_parser()
# turn off namepsaces so that startElement and endElement 
# are called for every tag
# parser.setFeature(xml.sax.handler.feature_namespaces, 0)
# change the handler
# Handler = WikiDumpHandler()
# parser.setContentHandler(Handler)
# done = 1
initial = time.time()
# for file in os.listdir(wiki_dump_path):
	# if file[0] != '.':
		# start = time.time()
		# parser.parse(str(wiki_dump_path)+str(file))
		# print("Done " + str(done))
		# print("Time taken = " + str(time.time() - start))
		# print("Total time taken = " + str(time.time() - initial))
		# done += 1
# 
# print remaining entries
# printIndex = PrintToFile()
# printIndex.output_to_file()
# TitleObject = TitlesFile()
# TitleObject.output_to_file()		
# print("remaining done")
# with open("total.txt","w") as out:
	# out.write(str(total_documents))
# merge files
mergeObject = Merge()
mergeObject.mergeFiles()
print("Total time taken = " + str(time.time() - initial))