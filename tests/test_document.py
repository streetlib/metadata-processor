# -*- coding: UTF-8 -*-

import	unittest
from	fragments	import	*
from	document	import	*

class DocumentTests (unittest.TestCase):

	def fragment(self, lineNumber, range, text, attributes):
		if range:
			result = LineChunkFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), lineNumber, range, text, attributes)
		else:
			result = WholeLineFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), (lineNumber, lineNumber), text, attributes)

		return result

	def test_normalizedFragments (self):
		content = [
			"Title",
			"Some text, with more words here.",
		]
		metadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (6, 10), "text", {'tags':['tag']}),
			self.fragment(2, (22, 27), "words", {'tags':['tag']})
		]

		normalizedMetadata = Document.normalizeFragments(content, metadata)

		expectedMetadata = [
			self.fragment(0, (1, 7), "Title\n", {'style':'Heading 1'}),
			self.fragment(0, (12, 16), "text", {'tags':['tag']}),
			self.fragment(0, (28, 33), "words", {'tags':['tag']})
		]

		self.assertEqual(expectedMetadata, normalizedMetadata)


	def test_rebaseFragments (self):
		content = [
			"Title",
			"Some text, with more words here.",
		]

		metadata = [
			self.fragment(0, (1, 7), "Title\n", {'style':'Heading 1'}).normalize([0]),
			self.fragment(0, (12, 16), "text", {'tags':['tag']}).normalize([0]),
			self.fragment(0, (28, 33), "words", {'tags':['tag']}).normalize([0])
		]

		rebasedMetadata = Document.rebaseFragments(content, metadata)

		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (6, 10), "text", {'tags':['tag']}),
			self.fragment(2, (22, 27), "words", {'tags':['tag']})
		]

		self.assertEqual(expectedMetadata, rebasedMetadata)


	def test_mergeDocumentsWithSimpleInsertedText (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"Some text, with more words here.",
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (6, 10), "text", {'tags':['tag']}),
				self.fragment(2, (22, 27), "words", {'tags':['tag']})
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"Some text, extra text added here, with more words here.",
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (6, 10), "text", {'tags':['tag']}),
			self.fragment(2, (45, 50), "words", {'tags':['tag']})
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())


	def test_mergeDocumentsWithInsertedTextInsideTag (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"Some text, with more words here.",
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (6, 27), "text, with more words", {'tags':['tag']}),
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"Some text, extra text added here, with more words here."
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (6, 50), "text, extra text added here, with more words", {'tags':['tag']}),
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())


	def test_mergeDocumentsWithSimpleInsertNewParagraph (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"Some text, with more words here."
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (6, 10), "text", {'tags':['tag']}),
				self.fragment(2, (22, 27), "words", {'tags':['tag']})
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
			"Title",
			"Extra paragraph added here",
			"Some text, with more words here."
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(3, (6, 10), "text", {'tags':['tag']}),
			self.fragment(3, (22, 27), "words", {'tags':['tag']})
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())

	# =========================================================================

	def test_mergeDocumentsWithSimpleDeletedText (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"Some text, with more words here.",
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (6, 10), "text", {'tags':['tag']}),
				self.fragment(2, (22, 27), "words", {'tags':['tag']})
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"Some text, more words here.",
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (6, 10), "text", {'tags':['tag']}),
			self.fragment(2, (17, 22), "words", {'tags':['tag']})
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())


	def test_mergeDocumentsWithDeletedTextInsideTag (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"Some text, with more words here."
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (6, 27), "text, with more words", {'tags':['tag']}),
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"Some text words here."
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (6, 16), "text words", {'tags':['tag']}),
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())


	def test_mergeDocumentsWithDeletedTextAtTheBeginningOfTag (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"Some text, with more words here."
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (6, 21), "text, with more", {'tags':['tag']}),
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"more words here."
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (1, 5), "more", {'tags':['tag']}),
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())


	def test_mergeDocumentsWithDeletedTextAtTheEndOfTag (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"Some text, with more words here."
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (6, 21), "text, with more", {'tags':['tag']}),
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"Some text, here."
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (6, 11), "text,", {'tags':['tag']}),
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())


	def test_mergeDocumentsWithSimpleDeleteOfParagraph (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"Some text, with more words here.",
				"An extra paragraph here"
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (6, 10), "text", {'tags':['tag']}),
				self.fragment(2, (22, 27), "words", {'tags':['tag']}),
				self.fragment(3, (10, 19), "paragraph", {'tags':['tag']})
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"An extra paragraph here"
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (10, 19), "paragraph", {'tags':['tag']})
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())

	# -------------------------------------------------------------------------

	def test_mergeDocumentsWithMergedParagraphs (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"First paragraph here.",
				"Second paragraph here.",
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (1, 6), "First", {'tags':['tag']}),
				self.fragment(3, (1, 7), "Second", {'tags':['tag']}),
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"First paragraph here. Second paragraph here.",
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (1, 6), "First", {'tags':['tag']}),
			self.fragment(2, (23, 29), "Second", {'tags':['tag']}),
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())


	def test_mergeDocumentsWithSplittedParagraphs (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"First sentence here. Second sentence here.",
			], None, [
				self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
				self.fragment(2, (1, 6), "First", {'tags':['tag']}),
				self.fragment(2, (22, 28), "Second", {'tags':['tag']}),
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Title",
				"First sentence here.",
				"Second sentence here.",
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, None, "Title\n", {'style':'Heading 1'}),
			self.fragment(2, (1, 6), "First", {'tags':['tag']}),
			self.fragment(3, (1, 7), "Second", {'tags':['tag']}),
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())

	# -------------------------------------------------------------------------

	def test_mergeDocumentsWithMultipleDiffs_firstInsertThanDelete (self):
		document =	Document().initWithDocumentInfo([
				"First sentence here. Second sentence here.",
			], None, [
				self.fragment(1, (1, 6),	"First",	{'tags':['tag']}),
				self.fragment(1, (22, 28),	"Second",	{'tags':['tag']}),
				self.fragment(1, (38, 42),	"here",		{'tags':['tag']}),
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"First sentence goes here. Second here.",
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(1, (1, 6),	"First",	{'tags':['tag']}),
			self.fragment(1, (27, 33),	"Second",	{'tags':['tag']}),
			self.fragment(1, (34, 38),	"here",		{'tags':['tag']}),
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())

	# =========================================================================

	def test_lineBreak_options (self):
		document =	Document().initWithDocumentInfo([
				"A mia sorella che ha letto le meditazioni\rAlle persone che mi hanno insegnato a meditare e a crescere\rAi miei gatti, piccoli grandi guru",
				"A mia sorella che ha letto le meditazioni\x0DAlle persone che mi hanno insegnato a meditare e a crescere\x0DAi miei gatti, piccoli grandi guru"
			], None, None
		)

		self.assertEqual(document.content()[0], document.content()[1])

	# =========================================================================

	def test_wholeLineFragmentAdjustmentWhenMergingNewVersion (self):
		document =	Document().initWithDocumentInfo([
				"Title",
				"First sentence here.",
				"Chater",
				"Second chapter content.",
				"Long title",
				"Other content"
			], None, [
				self.fragment(1, None, "Title\n", {}),
				self.fragment(3, None, "Chater\n", {}),
				self.fragment(5, None, "Long title\n", {}),
			]
		)

		updatedDocument = Document().initWithDocumentInfo([
				"Preface …",
				"Title",
				"First sentence here.",
				"Chapter",
				"Second chapter content.",
				"Short title",
				"Other content"
			], None, None
		)

		mergedDocument = document.mergeWithDocument(updatedDocument)
		expectedMetadata = [
			self.fragment(2, None, "Title\n", {}),
			self.fragment(4, None, "Chapter\n", {}),
			self.fragment(6, None, "Short title\n", {}),
		]
		self.assertEqual(expectedMetadata, mergedDocument.metadata())

	# =========================================================================

	def test_readContentWithBreakLines (self):
		document = Document().initWithFile(os.path.join(os.getcwd(), 'samples', 'expected outcome', 'docx', 'test_10'))

		self.assertEquals("""Paragraph 1 - Line 1\rParagraph 1 - Line 2\rParagraph 1 - Line 3\rParagraph 1 - Line 4""", document.content()[0])
		self.assertEquals("""Paragraph 2 - Line 1\rParagraph 2 - Line 2""", document.content()[1])

	# =========================================================================

#	def test_mergeDocumentsWithSwappedParagraphs (self):
#		document =	Document().initWithDocumentInfo([
#				"Title 1",
#				"Some text, with more words here.",
#				"Title 2",
#				"Text of second chapter here"
#			], None, [
#				self.fragment (1, None, "Title 1", {'style':'Heading 1'}),
#				self.fragment (2, (6, 10), "text", {'tags':['tag']}),
#				self.fragment (2, (22, 27), "words", {'tags':['tag']}),
#				self.fragment (3, None, "Title 2", {'style':'Heading 2'}),
#				self.fragment (4, (9, 28), "second chapter here", {'tags':'tag'}),
#			]
#		)
#
#		updatedDocument = Document().initWithDocumentInfo([
#				"Title 2",
#				"Text of second chapter here",
#				"Title 1",
#				"Some text, with more words here."
#			], None, None
#		)
#
#		mergedDocument = document.mergeWithDocument(updatedDocument)
#		expectedMetadata = [
#			self.fragment (1, None, "Title 2", {'style':'Heading 2'}),
#			self.fragment (2, (9, 28), "second chapter here", {'tags':'tag'}),
#			self.fragment (3, None, "Title 1", {'style':'Heading 1'}),
#			self.fragment (4, (6, 10), "text", {'tags':['tag']}),
#			self.fragment (5, (22, 27), "words", {'tags':['tag']}),
#		]
#		self.assertEqual(expectedMetadata, mergedDocument.metadata())
