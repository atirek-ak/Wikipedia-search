import os,sys
import xml.sax
import re
from collections import defaultdict
from nltk.corpus import stopwords
import Stemmer

inverted_index_path = str(sys.argv[1])
query = sys.argv[2]
stemmer = Stemmer.Stemmer('english')
stopwords = set(stopwords.words('english'))

class Search:
	def __init__(self, query):
		self.file = query
		self.query = ""
		self.k = 0
		self.words = []
		self.categories = ['g']
		self.data = []
		self.found = 0

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
				line = file.readline()
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
			data = line.split(' ')[1:]
			data = [w.strip() for w in data if category in w]
			print(data)
			# print(category)
		else:
			print("not found")	
			
	def splitSearch(self):
		global stopwords
		global stemmer
		with open(self.file,"r") as read_file:
			self.query = read_file.readline().strip()
			while self.query.strip() != "":
				# print(self.query)
				self.k = self.query.split(',')[0]
				# print(self.k)
				self.words = self.query.split(',')[1].split(':')
				# print(self.words)
				# words = words.split(":")
				# print(words)
				self.categories = ['g']
				for i in range(0, len(self.words)-1):
					# print(i)
					self.categories.append(self.words[i][-1])
					self.words[i] = self.words[i][:-1]
				# print(self.categories)
				# print(self.words)
				for i in range(0, len(self.words)):
					word = self.words[i]
					self.data = word.split(' ')
					self.data = [w.lower() for w in self.data if w.lower() not in stopwords]
					self.data = stemmer.stemWords(self.data)
					# print(self.data)
					self.words[i] = ' '.join(self.data).strip()
					# print(self.words[i])
				# print(self.words)	
				# print(self.categories)
				for i in range(0, len(self.words)):
					self.search(self.words[i], self.categories[i])
				# for i in range(0, len(words)):
				self.query = read_file.readline().strip()



searchObject = Search(query)
searchObject.splitSearch()