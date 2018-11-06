import spacy
from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer
import re

sentences = 'His hair was so black'


class Qgen:

	def __init__(self, sentence):
		self.all_possible_tags = set(['VBD', 'VBG', 'VBN', 'VB', 'VBZ'])
		self.text = self._clean(sentence)
		self.tags = TextBlob(self.text).tags
		self.question = None
		self.question_tag = None
		self.formated = str()
		self.genq()
		self._format_question()

	def _clean(self, sentence):
		text = re.sub(r'”|“|’|"', '', sentence)
		return text.lower()
	def _generate_quest(self, item, index):
		# import ipdb; ipdb.set_trace()
		flag = True
		if len(item) <= index + 1:
			return

		elif item[index + 1][1] not in self.all_possible_tags:
			return
		self.question = 'Who '
		if item[index + 1][1] in ['VBG']:
			self.question = 'Who is '
		if item[index][1] in ['PRP$']:
			self.question = 'Whose '
		if item[index][1] in ['NN'] and item[index][0] not in ['i','ive'] and item[index + 1][0] not in ['is']:
			self.question = 'What '
		if item[index][0] in ['it']: #and item[index + 1][0] in ['is']:
			self.question = 'What '
		for i in range(index + 1, len(item)):
			self.question += item[i][0] + ' '


	def genq(self):
		print(self.tags)
		for index, item in enumerate(self.tags):
			if item[1] in ['NN', 'NNS', 'PRP', 'NNP', 'NNPS', 'PRP$']:
				self._generate_quest(self.tags, index)
				break

	def _format_question(self):
		if self.question:
			self.question_tags = TextBlob(self.question).tags
		else:
			return	
		for index, tag in enumerate(self.question_tags):
			# print(tag, index)
			# import ipdb; ipdb.set_trace()
			if tag[1] in ['VBD', 'VB', 'VBG', 'VBN'] and self._can_preseed_verb(index):
				self.formated += ' will ' + WordNetLemmatizer().lemmatize(tag[0], 'v')
			elif tag[1] in ['NNP', 'PRP'] and index != 0 or tag[0] == 'i':  # Noune and personal pronoun: she, he, it, they
				self.formated += ' someone'
			elif tag[1] in ['PRP$']:  # Possessive pronoun:  her, his , mine
				self.formated += ' their'
			elif tag[1] in ['POS']:
				self.formated += tag[0]
			elif tag[0] in ['this', 'these']:
				continue       # determinor: these, this
			else:
				self.formated += ' ' + tag[0]
		
	def _can_preseed_verb(self, index):
		if index == len(self.question_tags) - 1: # last word
			return False
		if index == 0:
			return True
		else:
			if self.question_tags[index -1 ][1] in ['WP']:
				return True
		return False


def main():
	with open('novel.txt', 'r') as fp:
		novel = fp.read()

	for elem in re.split(r'\.|,\n', novel):                                                                       
		sentence = elem.rstrip().lstrip()                                        
		if sentence != '':                                      
			q = Qgen(sentence)
			if q.question:
				print("Text: ", q.text)
				print("Question: ", q.question)
				print("Formated:", q.formated)
				print('-'*20)
				print('\n')

if __name__ == '__main__':
	main()
