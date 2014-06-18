# -*- coding: UTF-8 -*-

import	zipfile
from	lxml		import	etree
from	collections	import	defaultdict

from	fragments	import	*
from	document	import	Document

def LINE_BREAK ():
	return '\r'		# '\x0D'

def PARAGRAPH_BREAK ():
	return '\n'


class DocxProcessor:

	def __init__ (self, aDocxDocument):
		self._docxDocument = aDocxDocument

		doc = zipfile.ZipFile(self._docxDocument)
		self._word_document	= etree.fromstring(doc.read('word/document.xml'))
		self._word_styles	= etree.fromstring(doc.read('word/styles.xml'))
		
		self._paragraphStyleMapping = None
		self._document = None

	#---------------------------------------------------------

	def document (self):
		if not self._document:
			paragraphs = self._word_document.findall('.//' + fullyQualifiedName('w','p'))
			documentInfo, formatting = self._processParagraphs(paragraphs)

			content = []
#			formatting = []
			for paragraphInfo in documentInfo:
				if paragraphInfo:
					content.append(paragraphInfo['content'])
					for tag in paragraphInfo['tags']:
						formatting.append(tag)

			self._document = Document().initWithDocumentInfo(content, formatting, None)

		return self._document

	#---------------------------------------------------------

	def _processParagraphs (self, paragraphs):
		paragraphInfos = []
		paragraphBlocks = []
		paragraphBlockStart = 0
		consecutiveNumberOfEmptyLines = 0

		def checkWhetherALineBlockNeedsToBeAdded (currentLineNumber, checkWholeDocumentRange = False):
			if paragraphBlockStart == 0 and checkWholeDocumentRange:
				pass
			elif paragraphBlockStart < currentLineNumber:
				paragraphBlockContent = ''
				for i in range(paragraphBlockStart, currentLineNumber):
					paragraphBlockContent += paragraphInfos[i]['content'] + PARAGRAPH_BREAK()
				paragraphBlocks.append(WholeLineFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), (paragraphBlockStart + 1, currentLineNumber), paragraphBlockContent, {'structure': 'line-block'}))

		for paragraph in paragraphs:
			currentLineNumber = len(paragraphInfos)
			paragraphInfo = self._processParagraph(currentLineNumber + 1, paragraph)

			if paragraphInfo:
				paragraphInfos.append(paragraphInfo)

				if consecutiveNumberOfEmptyLines > 4:
					paragraphBlocks.append(LineChunkFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), currentLineNumber + 1, (1, 1), "", {'structure': 'possible-page-break'}))

				consecutiveNumberOfEmptyLines = 0
			else:
				checkWhetherALineBlockNeedsToBeAdded(currentLineNumber)
				paragraphBlockStart = currentLineNumber
				consecutiveNumberOfEmptyLines += 1

		checkWhetherALineBlockNeedsToBeAdded(len(paragraphInfos), True)

		return paragraphInfos, paragraphBlocks


	def _textRunText (self, textRunElement):
		result = ''

		for element in textRunElement.iter():
			if element.tag == fullyQualifiedName('w', 't'):		# 't' (text) elements
				if element.text:
					result = result + element.text
			elif element.tag == fullyQualifiedName('w', 'br'):	# 'br' (break line) elements
				result = result + LINE_BREAK()
			elif element.tag == fullyQualifiedName('w', 'tab'):
				result = result + '\t'

		return result


	def _cleanupTextAndTags (self, text, tags, lineNumber):
		cleanText = ' '.join(text.split())
		cleanTags = []

		if cleanText != text:

			diffs = Document.computeDiffs(text, cleanText)
			translationMap = Document.computeTranslationMap(diffs)

			for tag in tags:
				updatedTag = tag.updateWithTranslationMap(translationMap)
				if updatedTag:
					cleanTags.append(updatedTag.setLine(lineNumber))
		else:
			for tag in tags:
				cleanTags.append(tag.setLine(lineNumber))

		return cleanText, cleanTags


	def _processParagraph (self, lineNumber, paragraph):
		paragraphText = ''
		tags = []

		for textRun in paragraph.findall('./' + fullyQualifiedName('w','r')):
			runText = self._textRunText(textRun)
			if runText:
				runTextPosition = len(paragraphText) + 1
				paragraphText += runText
				style = self._textRunStyle(textRun)
				if style:
					runRange = (runTextPosition, runTextPosition + len(runText))
					tags.append(NormalizedFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), runRange, runText, style))

		paragraphText = paragraphText.replace(LINE_BREAK(), u'\uE000')
		paragraphText, tags = self._cleanupTextAndTags(paragraphText, tags, lineNumber)
		paragraphText = paragraphText.replace(u'\uE000', LINE_BREAK())
		paragraphStyle = self._paragraphStyle(paragraph)
		if paragraphStyle and paragraphStyle != 'Default Style':
			tags.append(WholeLineFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), (lineNumber, lineNumber), paragraphText + PARAGRAPH_BREAK(), {'style':self._paragraphStyle(paragraph)}))

		if not len(paragraphText) == 0:
			result = {'content': paragraphText, 'tags':tags}
		else:
			result = None
			
		return result


	def _paragraphStyle (self, paragraph):
		paragraphStyleElement = paragraph.find('./' + fullyQualifiedName('w','pPr') + '/' + fullyQualifiedName('w', 'pStyle'))
		if paragraphStyleElement is not None:
			paragraphStyle = paragraphStyleElement.get(fullyQualifiedName('w', 'val'))
			result = self._lookupParagraphStyle(paragraphStyle)
		else:
			result = None

		return result


	def _textRunStyle (self, textRunElement):
		formattings = []
		textRunProperties = textRunElement.find('./' + fullyQualifiedName('w','rPr'))

		for textRunProperty in textRunProperties:
			if textRunProperty.tag == fullyQualifiedName('w','u'):
				formattings.append('underline')
			if textRunProperty.tag == fullyQualifiedName('w','i'):
				formattings.append('italic')
			if textRunProperty.tag == fullyQualifiedName('w','b'):
				formattings.append('bold')
		
		if formattings:
			result = {'formattings': formattings}
		else:
			result = None
			
		return result


	def _lookupParagraphStyle (self, paragraphStyle):
		mapping = self.paragraphStyleMapping()
		
		if paragraphStyle in mapping:
			result = mapping[paragraphStyle]
		else:
			result = None
			
		return result

	#---------------------------------------------------------

	def paragraphStyleMapping (self):
		if not self._paragraphStyleMapping:
			self._paragraphStyleMapping = {}

			styles = [element
				for element in self._word_styles.iter()
				if element.tag == fullyQualifiedName('w','style')
				and element.get(fullyQualifiedName('w','type')) == 'paragraph'
			]

			for style in styles:
				key = style.get(fullyQualifiedName('w','styleId'))
				value = style.find('./' + fullyQualifiedName('w','name')).get(fullyQualifiedName('w', 'val'))
				self._paragraphStyleMapping[key] = value

		return self._paragraphStyleMapping

#=============================================================

nsprefixes = {
	'mo':		'http://schemas.microsoft.com/office/mac/office/2008/main',
	'o':		'urn:schemas-microsoft-com:office:office',
	've':		'http://schemas.openxmlformats.org/markup-compatibility/2006',

	# Text Content
	'w':		'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
	'w10':		'urn:schemas-microsoft-com:office:word',
	'wne':		'http://schemas.microsoft.com/office/word/2006/wordml',

	# Drawing
	'a':		'http://schemas.openxmlformats.org/drawingml/2006/main',
	'm':		'http://schemas.openxmlformats.org/officeDocument/2006/math',
	'mv':		'urn:schemas-microsoft-com:mac:vml',
	'pic':		'http://schemas.openxmlformats.org/drawingml/2006/picture',
	'v':		'urn:schemas-microsoft-com:vml',
	'wp':		'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',

	# Properties (core and extended)
	'cp':		'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
	'dc':		'http://purl.org/dc/elements/1.1/',
	'ep':		'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
	'xsi':		'http://www.w3.org/2001/XMLSchema-instance',

	# Content Types (we're just making up our own namespaces here to save time)
	'ct':		'http://schemas.openxmlformats.org/package/2006/content-types',

	# Package Relationships (we're just making up our own namespaces here to save time)
	'r':		'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
	'pr':		'http://schemas.openxmlformats.org/package/2006/relationships',

	# Dublin Core document properties
	'dcmitype':	'http://purl.org/dc/dcmitype/',
	'dcterms':	'http://purl.org/dc/terms/',
}

def fullyQualifiedName (namespace, name):
	return '{' + nsprefixes[namespace] + '}' + name
