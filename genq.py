import spacy
from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer
import re

sentences = 'His hair was so black'


class Qgen:

	# _isprp_it = lambda self, tag: True if tag[1] == 'PRP' and tag[0] == 'it'
	# False if tag
	def _isprp_it(self, tag):
		if tag[0] == 'PRP':
			if tag[0] == 'it':
				return True
			else:
				return False

		elif tag[0] != 'PRP':
			return True

	def __init__(self, sentence):
		self.all_possible_tags = set(['VBD', 'VBG', 'VBN', 'VB', 'VBZ'])
		self.text = self._clean(sentence)
		self.tags = TextBlob(self.text).tags
		self.question = None
		self.question_tag = None
		self._tag_collection = list()  # to chek if the tags can form a question
		self.formated = str()
		self._new_sentences = list()
		self.genq()
		self._format_question()
		# self._rules_for_qestion = [
		#     ['NNS',]
		# ]

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
		if item[index][1] in ['NN'] and item[index][0] not in ['i', 'ive'] and item[index + 1][0] not in ['is']:
			self.question = 'What '
		if item[index][0] in ['it']:  # and item[index + 1][0] in ['is']:
			self.question = 'What '
		for i in range(index + 1, len(item)):
			self.question += item[i][0] + ' '

	def _can_form_question(self):
		return False

	def genq(self):
		for index, item in enumerate(self.tags):
			if self._can_form_question():
				self._new_sentences.append(' '.join(self.tags[index:]))
				break
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
			# if tag[0] == 'you':
			# import ipdb	; ipdb.sset_trace()

			if tag[1] in ['VBD', 'VB', 'VBG', 'VBN', 'PRP', 'VBP', 'VBZ', 'VBP'] and self._can_preseed_verb(index):
				self.formated += ' will ' + \
					WordNetLemmatizer().lemmatize(tag[0], 'v')
			# Noune and personal pronoun: she, he, it, they
			elif (tag[1] in ['NNP', 'PRP'] and index != 0 and self._isprp_it(tag)) or tag[0] == 'i':
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
		if index == len(self.question_tags) - 1 and len(self.question_tags) > 2:  # last word
			return False
		if index == 0:
			return True
		if self.question_tags[index][0] in ['ill']:
			return False
		if len(self.question_tags) -1 != index and self.question_tags[index +1][1] in ['VBP']:
			return False
		else:
			if self.question_tags[index - 1][1] in ['WP','PRP']:
				return True
		return False


def main():
	# sent = 'he suggests'
	sent = None
	if sent:
		q= Qgen(sent)
		print("Tags:", q.tags)
		print("Text: ", q.text)
		print("Question: ", q.question)
		print("Formated:", q.formated)
		print("Question tags:", q.question_tags)
		print('-' * 20)
		print('\n')
		return

	with open('novel.txt', 'r') as fp:
		novel = fp.read()

	for elem in re.split(r'\.|,\n|\?|—', novel):
		sentence = elem.rstrip().lstrip()
		if sentence != '':
			q = Qgen(sentence)
			if q.question:
				print("Tags:", q.tags)
				print("Text: ", q.text)
				print("Question: ", q.question)
				print("Formated:", q.formated)
				print("Question tags:", q.question_tags)
				print('-' * 20)
				print('\n')

if __name__ == '__main__':
	main()
