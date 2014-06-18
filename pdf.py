# -*- coding: UTF-8 -*-

from	fragments	import	*
from	document	import	Document

from	pdfminer.pdfparser	import	PDFParser, PDFDocument
from	pdfminer.pdfinterp	import	PDFResourceManager, PDFPageInterpreter, process_pdf
from	pdfminer.pdfdevice	import	PDFDevice
from	pdfminer.converter	import	TextConverter
from	pdfminer.layout		import	LAParams
from	cStringIO			import	StringIO

class PdfProcessor:

	def __init__ (self, aPdfDocument):
		self._pdfDocument = aPdfDocument
		self._document = None

	#---------------------------------------------------------

	def document (self):

		def mergeSameParagraphLines (lines):
			def isEndOfParagraph (line):
				return line[-1:] in ['.', '?', '!'] or len(line) < 60

			result = []
			currentLine = ''

			for line in lines:
#				print "# '" + line + "'"
				currentLine += line
				if isEndOfParagraph(line):
					result.append(currentLine)
					currentLine = ''

			if currentLine != '':
				result.append(currentLine)

			return result

		if not self._document:
			pdfFile = open(self._pdfDocument, 'rb')
			pdfParser = PDFParser(pdfFile)
			document = PDFDocument()

			pdfParser.set_document(document)
			document.set_parser(pdfParser)
			document.initialize()

			if not document.is_extractable:
				raise pdfminer.pdfparser.PDFTextExtractionNotAllowed

			resourceManger = PDFResourceManager()

			debug = 1
			#
			PDFDocument.debug = debug
			PDFParser.debug = debug
#			CMapDB.debug = debug
			PDFResourceManager.debug = debug
			PDFPageInterpreter.debug = debug
			PDFDevice.debug = debug
			#

			pdfContent = StringIO()
			laparams = LAParams()
			laparams.all_texts = True
			laparams.detect_vertical = True
#			laparams.line_margin = 1.0
#			laparams.char_margin = 1.0
#			laparams.word_margin = 1.0
#			laparams.boxes_flow = 1.0

#			device = PDFDevice(resourceManger)
			device = TextConverter(resourceManger, pdfContent, codec='utf-8', laparams=laparams)
			interpreter = PDFPageInterpreter(resourceManger, device)
			for page in document.get_pages():
				interpreter.process_page(page)
			content = mergeSameParagraphLines(pdfContent.getvalue().split('\n'))

			toc = []
			try:
				for (level, title, destination, a, se) in document.get_outlines():
					toc.append((level, title))
			except:
				pass

			pdfContent.close()

			self._document = Document().initWithDocumentInfo(content, None, None)

		return self._document

