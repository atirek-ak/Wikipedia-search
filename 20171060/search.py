import os,sys
import xml.sax
import re
from collections import defaultdict
from nltk.corpus import stopwords
import Stemmer
import time
import numpy as np
import linecache

inverted_index_path = str(sys.argv[1])
query = sys.argv[2]
stemmer = Stemmer.Stemmer('english')
stopwords = set(stopwords.words('english'))

class Search:
	def __init__(self, query, total_documents):
		self.file = query
		self.query = ""
		self.k = 0
		self.words = []
		self.categories = ['g']
		self.data = []
		self.found = 0
		self.tfidf = defaultdict(float)
		self.total_documents = float(total_documents)
		self.title = defaultdict(list) # stores title
		self.num_tokens = defaultdict(int) # stores number of tokens in document

	def search(self, term, category):
		global inverted_index_path
		words = term.split(" ")
		# print(words)
		for word in words:
			if word == '':
				continue
			cur_file = 26
			while cur_file >= 1:
				read_file = inverted_index_path + str(cur_file) + ".txt"
				file = open(read_file,"r")
				line = file.readline().strip()
				first_word = line.split(' ')[0]
				if first_word > word:
					file.close()
					cur_file -= 1
				else:
					# print(word)
					# print(cur_file)
					self.getPostingList(line,file,word,category)
					file.close()
					break
					
		# print(lines)
		# print(words)
		# print(category)
		# for word in words:
			# data = []
			# if word == '':
				# continue
			# for line in lines:
				# print(line)
				# first = line.split(" ")[0]
				# first = first[0]
				# if first == word:
					# data = line.split(" ")
			# print(data)
			# final = []
			# if category == 'g':
				# final = data
			# else:	
				# for element in data:
					# if category in element:
						# final.append(element)
			# final = final[1:]
			# if len(final) > 0:
				# print("Postings for " + str(word) + " in " + str(category) + ":")
				# final[-1] = final[-1].replace('\n', '')
				# print(final)
				# print()

		# inverted_index_tokens = len(content.split("\n")) - 1
		# file.close()	

	def getPostingList(self,line,file,word,category):
		while word > line.split(' ')[0]:
			line = file.readline()
		if word == 	line.split(' ')[0]:
			# print(line)
			data = line.split(' ')
			# data = [w.strip() for w in data if category in w]
			self.getTFIDF(data, category)
			# print(data)
			# print(category)
		else:
			print(str(word) + " not found")	

	def getTFIDF(self, postings, category):
		word = postings[0]
		idf_word = np.log(self.total_documents / (len(postings)-1))
		for posting in postings[1:]:
			# print(posting)
			cpy = ""
			for ch in posting[1:]:
				if ch.isalpha():
					cpy = cpy + " " + ch
				else:
					cpy = cpy + ch	
			info = cpy.strip().split(' ')
			docID = int(info[0])
			if self.num_tokens[docID] == 0:
				self.getDocInfo(docID)
			tf = self.getWeight(info[1:], category)
			tf /= self.num_tokens[docID]
			# temp_title = ''.join(self.title[docID]).strip()
			self.tfidf[docID] += tf*idf_word


	def getWeight(self, info, category):
		weight = 0.0
		for term in info:
			times = term[1:]
			times = float(times)
			times = times/100
			field = term[:1]
			factor = 0.001
			if field == 't':
				factor = 0.25
			elif field == 'b':
				factor = 0.25
			elif field == 'i':
				factor = 0.20
			elif field == 'c':
				factor = 0.10
			elif field == 'r':
				factor = 0.05
			elif field == 'l':
				factor = 0.05
			if field == category:
				factor *= 1.5
			weight += factor*times
		return weight

	def getDocInfo(self, id):
		page_number = int((id-1)/100000 + 1)
		file_name = "./title/title" + str(page_number) + ".txt"
		# print(page_number)
		# print(id)
		line_number = int((id-1)%100000 + 1)
		line = linecache.getline(file_name,line_number).strip()
		line = ' '.join(line.split(' ')[1:])
		# print(line)
		tokens = int(''.join(line.split(":")[-1:]))
		# print(tokens)
		self.num_tokens[id] = tokens
		title = ':'.join(line.split(":")[:-1])
		# print(title)
		self.title[id].append(title)
		# print(self.title[id])



	def splitSearch(self):
		global stopwords
		global stemmer
		with open("queries_op.txt","w") as out:
			out.write("")
		with open(self.file,"r") as read_file:
			self.query = read_file.readline().strip()
			while self.query.strip() != "":
				start = time.time()
				self.k = int(self.query.split(',')[0])
				# self.k = 5
				self.tfidf = defaultdict(float)
				self.words = self.query.split(',')[1].split(':')
				self.categories = ['g']
				for i in range(0, len(self.words)-1):
					self.categories.append(self.words[i][-1])
					self.words[i] = self.words[i][:-1]
				for i in range(0, len(self.words)):
					word = self.words[i]
					self.data = word.split(' ')
					self.data = [w.lower() for w in self.data if w.lower() not in stopwords]
					self.data = stemmer.stemWords(self.data)
					self.words[i] = ' '.join(self.data).strip()
				for i in range(0, len(self.words)):
					self.search(self.words[i], self.categories[i])
				ans = sorted(self.tfidf.items(),key=lambda item: item[1], reverse=True)[:self.k]

				with open("queries_op.txt","a") as out:
					for item in ans:
						out.write(str(item[0]) + ", " + str(' '.join(self.title[item[0]])) + "\n")
					time_taken = time.time() - start
					out.write(str(time_taken) + ", " + str(time_taken/self.k) + "\n")
				self.query = read_file.readline().strip()


total_documents = 0
with open("total.txt", "r") as inp:
	total_documents = inp.readline()
# print(total_documents)	
searchObject = Search(query, total_documents)
searchObject.splitSearch()