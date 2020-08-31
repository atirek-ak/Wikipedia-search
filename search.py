import os,sys
import xml.sax
import re
from collections import defaultdict
from nltk.corpus import stopwords
import Stemmer

inverted_index_path = str(sys.argv[1])
query = sys.argv[2:]
stemmer = Stemmer.Stemmer('english')
stopwords = set(stopwords.words('english'))

class Search:
	def __init__(self, query):
		self.query = query

	def search(self, word, category):
		global inverted_index_path
		word = word.lower()
		words = word.split(" ")
		read_file = inverted_index_path + "index.txt"
		file = open(read_file,"r")
		lines = file.readlines() 
		# print(words)
		# print(category)
		for word in words:
			data = []
			if word == '':
				continue
			for line in lines:
				# print(line)
				first = line.split(" ")[0]
				# first = first[0]
				if first == word:
					data = line.split(" ")
			# print(data)
			final = []
			if category == 'g':
				final = data
			else:	
				for element in data:
					if category in element:
						final.append(element)
			final = final[1:]
			if len(final) > 0:
				print("Postings for " + str(word) + " in " + str(category) + ":")
				final[-1] = final[-1].replace('\n', '')
				print(final)
				print()

		# inverted_index_tokens = len(content.split("\n")) - 1
		file.close()	



			
	def splitSearch(self):
		words = ' '.join(self.query)
		words = words.split(":")
		# print(words)
		categories = ['g']
		for i in range(0, len(words)-1):
			categories.append(words[i][-1])
			words[i] = words[i][:-1]
		# print(categories)
		# print(words)
		for i in range(0, len(words)):
			word = words[i]
			data = word.split(' ')
			data = [w for w in data if w.lower() not in stopwords]
			data = stemmer.stemWords(data)
			# print(data)
			words[i] = ' '.join(data)
			# print(word)
		# print(words)	
		# print(categories)
		for i in range(0, len(words)):
			self.search(words[i], categories[i])
		# for i in range(0, len(words)):



searchObject = Search(query)
searchObject.splitSearch()