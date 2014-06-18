# -*- coding: UTF-8 -*-

import	unittest
from	fragments	import	*
from	document	import	*

class FragmentIdentifierTranslationMapTests (unittest.TestCase):

	def fragment(self, line):
		return FragmentIdentifier.fragmentWithLine(line).normalize([0])

	# =========================================================================

	def test_simpleFragmentTranslation (self):
	#	Some text, with more words here.
	#	     +--+  +-------+
	#	Some, with lot more words here.
	#
	#	0:[6-10] "text" - {}
	#	0:[12-21] "with more" - {}

		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Some text, with more words here.",
			#     +--+  +-------+
			"Some, with lot more words here."
			#      +-----------+
		))
		expectedTranslationMap = [
			( 1,  5,  0),
			(10, 17, -5),
			(17, 17, -5, 'lot '),
			(17, 33, -1)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[6-10] "text" - {}')
		expectedResult = None
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('0:[12-21] "with more" - {}')
		expectedResult = self.fragment('0:[7-20] "with lot more" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTranslationWithDeletionInsideTag (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Some text, with more words here.",
			#           +-------------+
			"Some text, with words here."
			#           +--------+
		))
		expectedTranslationMap = [
			(1, 17, 0),
			(22, 33, -5)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[12-27] "with more words" - {}')
		expectedResult = self.fragment('0:[12-22] "with words" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTranslationWithMultipleTagsAndDeletionInsideTag (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Title\nSome text, with more words here.",
			#+---+       +-------------------+
			"Title\nSome text, with words here."
			#+---+       +--------------+
		))
		expectedTranslationMap = [
			(1, 23, 0),
			(28, 39, -5)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[1-6] "Title" - {}')
		expectedResult = self.fragment('0:[1-6] "Title" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('0:[12-33] "text, with more words" - {}')
		expectedResult = self.fragment('0:[12-28] "text, with words" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTranslationWithDeletionOverlappingTagStart (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Title\nSome text, with more words here.",
			#            +-------------+
			"Title\nmore words here."
			#       +--+
		))
		expectedTranslationMap = [
			(1, 7, 0),
			(23, 39, -16)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[12-27] "text, with more" - {}')
		expectedResult = self.fragment('0:[7-11] "more" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTranslationWithDeletionOverlappingTagEnd (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Title\nSome text, with more words here.",
			#            +-------------+
			"Title\nSome text, here."
			#            +---+
		))
		expectedTranslationMap = [
			(1, 17, 0),
			(33, 39, -16)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[12-27] "text, with more" - {}')
		expectedResult = self.fragment('0:[12-17] "text," - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTranslationWithMultipleDeletionsInsideTag (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Some text, with more words here.",
			#	        +-------------+
			"Some text, wi more ds here."
			#	        +--------+
		))
		expectedTranslationMap = [
			(1, 14, 0),
			(16, 22, -2),
			(25, 33, -5)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[12-27] "with more words" - {}')
		expectedResult = self.fragment('0:[12-22] "wi more ds" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTranslationWithMultipleDeletionsInsideTag_2 (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Some AaaaA BbbbB CcccC DdddD EeeeE FfffF GgggG HhhhH",
			#     +---------------------------------------+
			"Some AaaaA CcccC EeeeE GgggG HhhhH"
			#     +---------------------+
		))
		expectedTranslationMap = [
#			(1, 12, 0),
#			(18, 24, -6),
#			(30, 36, -12),
#			(42, 53, -18)
			( 1, 12,   0),
			(41, 41, -29, 'CcccC EeeeE'),
			(41, 53, -18)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[6-47] "AaaaA BbbbB CcccC DdddD EeeeE FfffF GgggG" - {}')
		expectedResult = self.fragment('0:[6-29] "AaaaA CcccC EeeeE GgggG" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTranslationWithMultipleDeletionsInsideTag_3 (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Some AaaaaA BbbbbbB CccccccC DddddD EeeeeeeeE FfffffF GggggggG HhhhhhH",
			#     +-------------------------------------------------------+
			"Some AaaaaA CccccccC EeeeeeeeE GggggggG Word__H"
			#     +--------------------------------+
		))
		expectedTranslationMap = [
#			(1, 13, 0),
#			(21, 30, -8),
#			(37, 47, -15),
#			(55, 71, -23)
			(1, 13, 0),
			(21, 30, -8),
			(37, 47, -15),
			(55, 64, -23),
			(70, 70, -29, 'Word__'),
			(70, 71, -23)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[6-63] "AaaaaA BbbbbbB CccccccC DddddD EeeeeeeeE FfffffF GggggggG" - {}')
		expectedResult = self.fragment('0:[6-40] "AaaaaA CccccccC EeeeeeeeE GggggggG" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTranslationWithDeletionAndInsertion (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"First sentence here. Second sentence here.",
			#+---+                +----+          +--+
			"First sentence goes here. Second here."
			#+---+                     +----+ +--+
		))
		expectedTranslationMap = [
			( 1, 16,  0),
			(16, 16,  0,'goes '),
			(16, 29,  5),
			(38, 43, -4)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[1-6] "First" - {}')
		expectedResult = self.fragment('0:[1-6] "First" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('0:[22-28] "Second" - {}')
		expectedResult = self.fragment('0:[27-33] "Second" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('0:[38-42] "here" - {}')
		expectedResult = self.fragment('0:[34-38] "here" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_fragmentTrimmedAtTheEnd (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"  Paragraph with trailing and closing spaces      ",
			# ++-------------------------------------------+
			"Paragraph with trailing and closing spaces"
			#+----------------------------------------+
		))
		expectedTranslationMap = [
			(3, 45, -2)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('1:[1-2] " " - {}')
		expectedResult = None
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('1:[3-48] "Paragraph with trailing and closing spaces   " - {}')
		expectedResult = self.fragment('1:[1-43] "Paragraph with trailing and closing spaces" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_trimmedFragment (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"   Paragraph with trailing and closing spaces     ",
			# +--------------------------------------------+
			"Paragraph with trailing and closing spaces"
			#+----------------------------------------+
		))
		expectedTranslationMap = [
			(4, 46, -3)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('1:[2-48] "  Paragraph with trailing and closing spaces  " - {}')
		expectedResult = self.fragment('1:[1-43] "Paragraph with trailing and closing spaces" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_trimmedFragment_2 (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Some extra text.   Paragraph with trailing and closing spaces     ",
			#     +--------+
			#       +------+
			#                 +--------------------------------------------+
			"Some text. Paragraph with trailing and closing spaces"
			#     +--+
			#     +--+
			#           +----------------------------------------+
		))
		expectedTranslationMap = [
			(1, 6, 0),
			(12, 17, -6),
			(19, 62, -8)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('1:[6-16] "extra text" - {}')
		expectedResult = self.fragment('1:[6-10] "text" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('1:[8-16] "tra text" - {}')
		expectedResult = self.fragment('1:[6-10] "text" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('1:[18-64] "  Paragraph with trailing and closing spaces  " - {}')
		expectedResult = self.fragment('1:[11-54] " Paragraph with trailing and closing spaces" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_insertText (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Title\nSome text, with more words here.",
			#+---+	     +-------------------+
			"Title\nSome text, extra text added here, with more words here."
			#+---+	     +------------------------------------------+
		))
		expectedTranslationMap = [
			( 1, 17,  0),
			(17, 17,  0, ' extra text added here,'),
			(17, 39, 23)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[1-6] "Title" - {}')
		expectedResult = self.fragment('0:[1-6] "Title" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('0:[12-33] "text, with more words" - {}')
		expectedResult = self.fragment('0:[12-56] "text, extra text added here, with more words" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_insertTextAtTheVeryBeginningOfTag (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Title\nSome text, with more words here.",
			#+---+	     +-------------------+
			"Better title\nSome extra text, with more words here."
			#+----------+	    +-------------------------+
		))
		expectedTranslationMap = [
			(2, 2, -1, "Better t"),
			(2, 12, 7),
			(12, 12, 7, "extra "),
			(12, 39, 13)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[1-6] "Title" - {}')
		expectedResult = self.fragment('0:[1-13] "Better title" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('0:[12-33] "text, with more words" - {}')
		expectedResult = self.fragment('0:[19-46] "extra text, with more words" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_paragraphEditing (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Title\nFirst sentence here.\nChater\nSecond chapter content.\nLong title\nOther content",
			#                             +------+                         +----------+
			"Preface …\nTitle\nFirst sentence here.\nChapter\nSecond chapter content.\nShort title\nOther content"
			#                                        +-------+                         +-----------+
		))
		expectedTranslationMap = [
			( 1,  1,  0, 'Preface …\n'),
			( 1, 31, 12),
			(31, 31, 12, 'p'),
			(31, 59, 13),
			(63, 63,  9, 'Short'),
			(63, 83, 14)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[28-35] "Chater\n" - {}')
		expectedResult = self.fragment('0:[40-48] "Chapter\n" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)

		fragment = self.fragment('0:[59-70] "Long title\n" - {}')
		expectedResult = self.fragment('0:[72-84] "Short title\n" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_paragraphEditing_2 (self):
		translationMap = Document.computeTranslationMap(Document.computeDiffs(
			"Title\nFirst sentence here.\nChater\nSecond chapter content.\nLong title\nOther content",
			#                                                              +----------+
			"Preface …\nTitle\nFirst sentence here.\nShort title\nOther content"
			#                                        +-----------+
		))
		expectedTranslationMap = [
			( 1,  1,   0, 'Preface …\n'),
			( 1, 28,  12),
			(63, 63, -23, 'Short'),
			(63, 83, -18)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		fragment = self.fragment('0:[59-70] "Long title\n" - {}')
		expectedResult = self.fragment('0:[40-52] "Short title\n" - {}')
		updatedFragment = fragment.updateWithTranslationMap(translationMap)
		self.assertEqual(expectedResult, updatedFragment)


	def test_documentEditing (self):
		originalContent = [
			"Title",
			"First paragraph here.",
			"Second paragraph here.",
		]

		updatedContent = [
			"Title",
			"First paragraph here. Second paragraph here.",
		]
		translationMap = Document.computeTranslationMap(Document.computeDiffs(Document.contentToText(originalContent), Document.contentToText(updatedContent)))
		expectedTranslationMap = [
			( 1, 28,  0),
			(29, 29, -1, ' '),
			(29, 52,  0)
		]
		self.assertEquals(expectedTranslationMap, translationMap)

		metadata = [
			WholeLineFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), (1, 1), "Title\n", {'style':'Heading 1'}),
			LineChunkFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), 2, (1, 6), "First", {'tags':['tag']}),
			LineChunkFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), 3, (1, 7), "Second", {'tags':['tag']}),
		]

		normalizedMetadata = Document.normalizeFragments(originalContent, metadata)

		expectedNormalizedMetadata = [
			self.fragment('0:[1-7] "Title\n" - {\'style\':\'Heading 1\'}'),
			self.fragment('0:[7-12] "First" - {\'tags\':[\'tag\']}'),
			self.fragment('0:[29-35] "Second" - {\'tags\':[\'tag\']}'),
		]
		self.assertEquals(expectedNormalizedMetadata, normalizedMetadata)

#		updatedFragment = normalizedMetadata[0].updateWithTranslationMap(translationMap)
# 		expectedUpdatedFragment = self.fragment('0:[1-7] "Title\n" - {\'style\':\'Heading 1\'}')
# 		self.assertEqual(expectedUpdatedFragment, updatedFragment)
# 		rebasedFragment = Document.rebaseFragments(updatedContent, [updatedFragment])[0]
# 		expectedRebasedFragment = metadata[0]
# 		self.assertEquals(expectedRebasedFragment, rebasedFragment)
#
# 		updatedFragment = normalizedMetadata[1].updateWithTranslationMap(translationMap)
# 		expectedUpdatedFragment = self.fragment('0:[7-12] "First" - {\'tags\':[\'tag\']}')
# 		self.assertEqual(expectedUpdatedFragment, updatedFragment)
# 		rebasedFragment = Document.rebaseFragments(updatedContent, [updatedFragment])[0]
# 		expectedRebasedFragment = metadata[1]
# 		self.assertEquals(expectedRebasedFragment, rebasedFragment)

		updatedFragment = normalizedMetadata[2].updateWithTranslationMap(translationMap)
		expectedUpdatedFragment = self.fragment('0:[29-35] "Second" - {\'tags\':[\'tag\']}')
		self.assertEqual(expectedUpdatedFragment, updatedFragment)
		rebasedFragment = Document.rebaseFragments(updatedContent, [updatedFragment])[0]
		expectedRebasedFragment = LineChunkFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), 2, (23, 29), "Second", {'tags':['tag']})
		self.assertEquals(expectedRebasedFragment, rebasedFragment)
