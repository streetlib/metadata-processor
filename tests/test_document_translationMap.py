# -*- coding: UTF-8 -*-

import	unittest
from	document		import	*

class DocumentTranslationMapTests (unittest.TestCase):

	# =========================================================================

	def test_simpleDeletionInTheMiddle (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"Title\nmore words here."
		)
		expectedResult = [
			(1, 7, 0),
			(23, 39, -16)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	def test_simpleDeletionAtTheBeginning (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"Some text, with more words here.",
		)
		expectedResult = [
			(7, 39, -6)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	def test_simpleDeletionAtTheEnd (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"Title\n",
		)
		expectedResult = [
			(1, 7, 0)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	# =========================================================================

	def test_simpleInsertionInTheMiddle (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"Title\nSome text, extra note here, with more words here."
		)
		expectedResult = [
			( 1, 17,  0),
			(17, 17,  0, ' extra note here,'),
			(17, 39, 17)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	def test_simpleInsertionAtTheBeginning (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"New paragraph here.\nTitle\nSome text, with more words here.",
		)
		expectedResult = [
			(1, 39, 20)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	def test_simpleInsertionAtTheBeginning (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"Title\nSome text, with more words here.\nNew paragraph here.",
		)
		expectedResult = [
			( 1, 39, 0),
			(39, 39, 0, '\nNew paragraph here.')
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	# =========================================================================

	def test_simpleReplaceWithSameLength (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"Title\nSome text, with some words here.",
		)
		expectedResult = [
			( 1, 23,  0),
			(26, 26, -3, 'som'),
			(26, 39,  0)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	def test_simpleReplaceShorter (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"Title\nSome text, with two words here.",
		)
		expectedResult = [
			( 1, 23,  0),
			(27, 27, -4, 'two'),
			(27, 39, -1)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	def test_simpleReplaceLonger (self):
		diffs = Document.computeDiffs(
			"Title\nSome text, with more words here.",
			"Title\nSome text, with extra words here.",
		)
		expectedResult = [
			( 1, 23,  0),
			(27, 27, -4, 'extra'),
			(27, 39,  1)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	# =========================================================================

	def test_simpleDeleteAndInsert (self):
		diffs = Document.computeDiffs(
			"Some text, with more words here.",
			"Some, with many more words here.",
		)
		expectedResult = [
			(1, 5, 0),
			(10, 17, -5),
			(17, 17, -5, 'many '),
			(17, 33,  0)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	def test_simpleDeleteAndInsert_2 (self):
		diffs = Document.computeDiffs("Some text, with more words here.", "Some, with lot more words here.")
		expectedResult = [
			(1, 5, 0),
			(10, 17, -5),
			(17, 17, -5, 'lot '),
			(17, 33, -1)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))


	def test_simpleDeleteAndInsert_3 (self):
		diffs = Document.computeDiffs(
			"Title\nFirst sentence here.\nChater\nSecond chapter content.\nLong title\nOther content",
			"Preface …\nTitle\nFirst sentence here.\nChapter\nSecond chapter content.\nShort title\nOther content"
		)
		expectedResult = [
			( 1,  1,  0, 'Preface …\n'),
			( 1, 31, 12),
			(31, 31, 12, 'p'),
			(31, 59, 13),
			(63, 63,  9, 'Short'),
			(63, 83, 14)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	# =========================================================================

	def test_trim (self):
		diffs = Document.computeDiffs(
			"Some extra text.   Paragraph with trailing and closing spaces     ",
			"Some text. Paragraph with trailing and closing spaces",
		)
		expectedResult = [
			(1, 6, 0),
			(12, 17, -6),
			(19, 62, -8)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))

	def test_trim_2 (self):
		diffs = Document.computeDiffs(
			"   Paragraph with trailing and closing spaces     ",
			"Paragraph with trailing and closing spaces",
		)
		expectedResult = [
			(4, 46, -3)
		]
		self.assertEqual(expectedResult, Document.computeTranslationMap(diffs))
