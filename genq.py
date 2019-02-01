#!/usr/bin/env python
import os
import re
import json
import argparse
import pickle
import sys
import spacy
import PyPDF2
import magic
import glob

from textblob import TextBlob
from nltk.stem.wordnet import WordNetLemmatizer


class Qgen:

	def _isprp_it(self, tag):
		"""
		Chhecks if the tag is PRP and the value is it
		"""
		if tag[1] == 'PRP':
			if tag[0] == 'it':
				return True
			else:
				return False

		elif tag[0] != 'PRP':
			return True

	def __init__(self, sentence):
		self.all_possible_tags = set(['VBD', 'VBG', 'VBN', 'VB', 'VBZ']) # these are the verbs we will be using
		self.text = self._clean(sentence)
		self.tags = TextBlob(self.text).tags
		self.question = None
		self.question_tag = None
		self._tag_collection = list()  # to chek if the tags can form a question
		self.formated = str()
		self._new_sentences = list()
		self.genq()
		self._format_question()
		self._rules_for_qestion = [
			# ['NNP','']
		]

	def _clean(self, sentence):
		text = re.sub(r'”|“|’|"', '', sentence)
		return text.lower()

	def _generate_quest(self, item, index):
		"""
		Generates the question from the sentence.
		"""
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
		"""
		To Do: return true if the set of tags in self.question can form a gramatically correct question 
				else retrurn false
		"""
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
		"""
		Convert the question to the required generalized form. (future sentence and remove names)
		"""
		if self.question:
			self.question_tags = TextBlob(self.question).tags
		else:
			return
		for index, tag in enumerate(self.question_tags):
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
		"""
		Checks what values can presead the verb
		"""
		if index == len(self.question_tags) - 1 and len(self.question_tags) > 2:  # last word
			return False
		if index == 0:
			return True
		if self.question_tags[index][0] in ['ill', 'didnt', 'didnot', "did'nt"]:
			return False
		if len(self.question_tags) - 1 != index and self.question_tags[index + 1][1] in ['VBP']:
			return False
		else:
			if self.question_tags[index - 1][1] in ['WP', 'PRP']:
				return True
		return False


class InputProcess:

	def __init__(self, args):
		self.args = args
		self.file_type = magic.from_file(args.file, mime=True)
		self.start = args.start_page if args.start_page else 0
		self.end = args.number_of_pages if args.number_of_pages else 10
		self.end = -1 if args.all else self.end
		self.knowledge_base = '.base.pkl'
		self.out = args.output if args.output else 'questions.csv'
		self.question_set = self.get_question_set()
		self.counter = 0
		self.process_file()
		self.save_data()

	def save_data(self):
		"""
		Saves the metadata: text, questions, and formated questions as a json
		saves the output as csv
		"""
		if self.counter > 0:
			with open(self.knowledge_base, 'wb') as fp:
				pickle.dump(self.question_set, fp)
			print("Metadata saved successfully")

			with open('meta.json', 'w') as fp:
				json.dump(self.question_set, fp, indent=4)

			with open(self.out, 'w') as f:
				[f.write('{0}|{1}|{2}\n'.format(key, value[0].replace('\n', ' '), value[
						 1].replace('\n', ' '))) for key, value in self.question_set.items()]

	def get_question_set(self):
		"""
		Loads the knowledge base dictionary
		"""
		if not os.path.isfile(self.knowledge_base):
			return dict()
		else:
			with open(self.knowledge_base, 'rb')as fp:
				return pickle.load(fp)

	def process_text(self, text):
		for elem in re.split(r'\.|,\n|\?|—|,|:', text):
			sentence = elem.rstrip().lstrip()
			if sentence != '':
				q = Qgen(sentence)
				if q.question:
					self.question_set[q.formated] = [q.question, q.text]
					self.counter += 1
					print(f'processed {self.counter} questions')

					if self.args.verbose:
						print("Tags:", q.tags)
						print("Text: ", q.text)
						print("Question: ", q.question)
						print("Formated:", q.formated)
						print("Question tags:", q.question_tags)
						print('-' * 20)
						print('\n')

	def _process_pdf(self):

		try:
			_file = open(self.args.file, 'rb')
			fileReader = PyPDF2.PdfFileReader(_file)
		except Exception as e:
			print(e)
			return

		num_pages = fileReader.numPages

		if self.end == -1:
			self.end = num_pages

		print('Processing PDF file...')

		for page_number in range(self.start, self.end):
			print("Processing page: ", page_number)
			self.process_text(fileReader.getPage(page_number).extractText())

	def _process_text_file(self):
		try:
			with open(self.args.file, 'r') as fp:
				self.process_text(fp.read())
		except Exception as e:
			print(e)
			return

	def process_file(self):
		if self.file_type == 'application/pdf':
			self._process_pdf()
		elif self.file_type == 'text/plain':
			self._process_text_file()
		else:
			print("ERROR: unsupported file type: ", self.file_type)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-file', '-f', help='input file location')
	parser.add_argument('-output', '-o', help='output file location')
	parser.add_argument('-start_page', '-s', type=int, help='page to start reading from')
	parser.add_argument('-number_of_pages', '-n', type=int,
						help='number of pages to read')
	parser.add_argument(
		'--all', action='store_true', help='process all the pages from the start_page')
	parser.add_argument('--verbose', '-v', action='store_true', help='verbose')
	parser.add_argument('--dir', '-d', help='input directory')

	args = parser.parse_args()
	# import ipdb; ipdb.set_trace()
	if args.file == None and args.dir == None:
		parser.print_help(sys.stderr)
		print("Error: no input file given")
		return
	# import ipdb; ipdb.set_trace()
	if args.dir:
		files = glob.glob(args.dir + '/*.pdf')
		print(files)
		for file in files:
			args.file = file 
			InputProcess(args)
	else:
		InputProcess(args)

if __name__ == '__main__':
	main()
