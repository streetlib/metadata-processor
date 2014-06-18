# -*- coding: UTF-8 -*-

import	json
import	codecs
from	fragments	import	*
from	document	import	Document

class SubstanceProcessor:

	def __init__ (self):
		self._document = None

	def initWithString (self, jsonString):
		self._substanceDocument = json.loads(jsonString)
		return self

	def initWithFile (self, fileName):
		fileContent = codecs.open(fileName, 'r', 'utf-8').read()
		return self.initWithString(fileContent)

	#---------------------------------------------------------

	def document (self):
		if self._document == None:
			substanceContent = self._substanceDocument['content']
			content = []
			metadata = []

			head = substanceContent['head']
			node = substanceContent['nodes'][head]

			while node != None:
				content.append(node['content'])
				node['lineNumber'] = len(content)

				if node['type'] == 'heading':
#					headingStyle = LineChunkFragmentIdentifier().initWithDetails(len(content), None, node['content'], {'style': 'heading'})
					headingStyle = WholeLineFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), (len(content), len(content)), node['content'] + '\n', {'style': 'heading'})
#					print("HEADING: " + str(headingStyle))
					metadata.append(headingStyle)

				if node['next']:
					node = substanceContent['nodes'][node['next']]
				else:
					node = None

			for annotation in substanceContent['annotations'].values():
				node = substanceContent['nodes'][annotation['node']]
				lineNumber = node['lineNumber']
				range = (annotation['pos'][0] + 1, annotation['pos'][0] + annotation['pos'][1] + 1)
				text = node['content'][range[0] - 1:range[1] - 1]

				info = {}
				info['type'] = annotation['type']

				matchingComments = [comment for comment in substanceContent['comments'].values() if comment['annotation'] == annotation['id']]
				if len(matchingComments) == 1:
					comment = matchingComments[0]
					info['content'] = comment['content']
					info['created_at'] = comment['created_at']
					info['user'] = comment['user']

				fragment = LineChunkFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), lineNumber, range, text, {'annotation': info})

				metadata.append(fragment)

			self._document = Document().initWithDocumentInfo(content, None, metadata)

		return self._document

	#---------------------------------------------------------
