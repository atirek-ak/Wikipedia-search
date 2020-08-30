import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer('english')
stopwords = set(stopwords.words('english'))

def process_text(total_articles, arg_list, index_path):
	"""
	arg_list[0] -> title
	arg_list[1] -> content
	"""
	# print(total_articles)
	text = arg_list[1].split('==References==')
	if len(text) == 1:
		text = arg_list[1].split('== References == ')
	category_index = []
	external_links_index = []
	references_index = []
	infobox_index = getInfobox(text[0])	
	body_index = getBody(text[0])
	title_index = getTitle(arg_list[0])
	if len(text) != 1:
		category_index = get_category(text[1])	
		external_links_index = get_external_links(text[1])
		references_index = get_references(text[1])

	# store all words
	# words = []
	# for field in arg_list:
		# words.append(re.findall("[a-zA-Z]+",field))

def tokenize(data):
	data = data.encode("ascii", errors="ignore").decode()
	data = re.sub(r'http[^\ ]*\ ', r' ', data) # removing urls
	data = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ', data) # removing html entities
	data = re.sub(r'\—|\%|\$|\'|\||\.|\*|\[|\]|\:|\;|\,|\{|\}|\(|\)|\=|\+|\-|\_|\#|\!|\`|\"|\?|\/|\>|\<|\&|\\|\u2013|\n', r' ', data) # removing special characters
	return data.split()	

def removeStopWords(data):
	return [w for w in data if w.lower() not in stopwords and len(w)>1]

def stem(data):
	text = []
	for element in data:
		text.append(stemmer.stem(element))
	# return stemmer.stem(data)
	return text

def getTitle(text):
	data = tokenize(text)
	data = removeStopWords(data)
	data = stem(data)
	return data	

# get body
def getBody(text):
	data = re.sub(r'\{\{.*\}\}', r' ', text)
	data = tokenize(data)
	data = removeStopWords(data)
	data = stem(data)
	return data	

# extract info box
def getInfobox(text):
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
	data = tokenize(' '.join(info))
	data = removeStopWords(data)
	data = stem(data)
	return data

# extract category
def get_category(text):
	data = text.split('\n')
	# print(data)
	categories = []
	for line in data:
		if re.match(r'\[\[Category', line):
			categories.append(re.sub(r'\[\[Category:(.*)\]\]', r'\1', line))
		elif re.match(r'\[\[category', line):
			categories.append(re.sub(r'\[\[category:(.*)\]\]', r'\1', line))	
	data = tokenize(' '.join(categories))
	data = removeStopWords(data)
	data = stem(data)
	return data

# extract external links
def get_external_links(text):
	data = text.split('\n')
	links = []
	for line in data:
		if re.match(r'\*[\ ]*\[', line):
			links.append(line)
		
	data = tokenize(' '.join(links))
	data = removeStopWords(data)
	data = stem(data)
	return data

# extract references
def get_references(text):
	data = text.split('\n')
	refs = []
	for line in data:
		if re.search(r'<ref', line):
			refs.append(re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line))
	data = tokenize(' '.join(refs))
	data = removeStopWords(data)
	data = stem(data)
	return data
