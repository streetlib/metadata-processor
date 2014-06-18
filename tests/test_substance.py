# -*- coding: UTF-8 -*-

import	unittest
import	os
from	document	import	Document
from	substance	import	SubstanceProcessor

class SubstanceTests (unittest.TestCase):

	def test_sampleDocumentProcessing (self):
		sampleSubstanceFile = os.path.join(os.getcwd(), 'samples', 'substance', '01_sample.json')
		substanceProcessor = SubstanceProcessor().initWithFile(sampleSubstanceFile)
		document = substanceProcessor.document()
		expectedDocument = Document().initWithFile(os.path.join(os.getcwd(), 'samples', 'expected outcome', 'substance_01'))

		print("DOCUMENT METADATA: " + str(document.metadata()))
		self.assertEqual(expectedDocument.content(),	document.content())
		self.assertEqual(expectedDocument.metadata(),	document.metadata())



