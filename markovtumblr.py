import urllib.request as r
import json
import re, random
import pickle

chainlength = 2
stopword = "\x02"
maxwords = 30
markov = {}

def sanitize_message(message): #removes quotes from message and converts it all to lower case
    return re.sub('[\"\']', '', message)

def parse_sentence(msg):
	msg = sanitize_message(msg)
	if(msg):
		for w1, w2, w3 in split_message(msg):
			key = (w1, w2)
			if key in markov:
				markov[key].append(w3)
			else:
				markov[key] = [w3]

def split_message(msg):
	words = msg.split()

	if len(words) > chainlength:
		words.append(stopword)
		for i in range(len(words)-chainlength):
			yield words[i:i+chainlength+1]


def generate_message():
	key = random.choice(list(markov.keys()))
	seenwords = []
	for i in range(maxwords):
		seenwords.append(key[0])
		nextword = random.choice(markov[key])
		if nextword == stopword:
			break
		key = (key[1], nextword)
	return ' '.join(seenwords)

def markov_start():
	global markov
	f = open("markov.txt","w+b")
	try:
		markov = pickle.load(f)
	except EOFError:
		pass
	print("Pickle loaded")


##MARKOV END##

def splitParagraphIntoSentences(paragraph):
    ''' break a paragraph into sentences
        and return a list '''
    sentenceEnders = re.compile('[.!?]')
    sentenceList = sentenceEnders.split(paragraph)
    return sentenceList

def cleanhtml(raw_html):

  cleanr = re.compile('<.*?>')

  cleantext = re.sub(cleanr,'', raw_html)

  return cleantext

def preparecomment(comment):
	comment = cleanhtml(comment.replace("><",">\n<").replace("<br>","\n")).split("\n")
	for i in comment:
		i = splitParagraphIntoSentences(i)
		try:
			print(i)
			for x in i:
				parse_sentence(x.strip())
		except UnicodeEncodeError:
			print("Unprintable text received")
		





def main():
	markov_start()


	postcount = json.loads(r.urlopen(r.Request('http://api.tumblr.com/v2/blog/fruitsoftheape100.tumblr.com/info')).read().decode("utf-8"))['response']['blog']['posts']
	print(postcount)

	for j in range(postcount-20,0,-20):
		print("OFFSET: " + str(j))

		request = r.Request('http://api.tumblr.com/v2/blog/fruitsoftheape100.tumblr.com/posts?api_key=SOSMdtAOehZYvrLM3yYFiAyqwUwpeWR5WIJsQ66cXNPw3PQBcx&filter=raw&offset='+str(j))

		response = r.urlopen(request)
		kittens = response.read().decode("utf-8")
		j = json.loads(kittens)

		reblog = True
		for i in range(0,20): 
			kind = j['response']['posts'][i]['type']
			post = j['response']['posts'][i]
			try:
				if post['reblog']:
					reblog = True
			except Exception:
				reblog = False
			material = "" #stuff to be markovd
			print(kind + "><" + ("reblog" if reblog else "oc"))
			if reblog:
				if kind != "chat" and kind != "quote":
					preparecomment(post['reblog']['comment'])
			else: #IGNORING CHATS AND QUOTES
				if kind == "text": #has title and body. can be replied to
					preparecomment(post['body'])
				elif kind == "video": #video has caption. can be replied to
					preparecomment(post['caption'])
				elif kind == "audio": #audio has caption as well. can be replied to
					preparecomment(post['caption'])
				elif kind == "photo": #has caption. can be replied to
					preparecomment(post['caption'])
				elif kind == "link": #has excerpt, description (text body), title, and publisher. can be replied to
					preparecomment(post['excerpt'])
				elif kind == "answer": #has question and answer
					preparecomment(post['answer'])
	print("end")
	f = open("markov.txt", "wb")
	pickle.dump(markov, f)
	print(markov)

	for i in range(0,20):
		g=""
		while len(g.split(" ")) < 2:
			g=generate_message()
		print(g)


main()
#how 2 deal with caption chains:
#you only have to read the lowest level. 