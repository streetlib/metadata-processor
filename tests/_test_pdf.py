# -*- coding: UTF-8 -*-

# self.assertEqual(a, b) – check a and b are equal
# self.assertNotEqual(a, b) – check a and b are not equal
# self.assertIn(a, b) – check that a is in the item b
# self.assertNotIn(a, b) – check that a is not in the item b
# self.assertFalse(a) – check that the value of a is False
# self.assertTrue(a) – check the value of a is True
# self.assertIsInstance(a, TYPE) – check that a is of type “TYPE”
# self.assertRaises(ERROR, a, args) – check that when a is called with args that it raises ERROR


import	unittest
import	os
from	pprint		import	pprint

from	pdf			import	PdfProcessor
from	document	import	Document
from	fragments	import	*

class PdfTests (unittest.TestCase):

	def test_parseSimplePdf (self):
		samplePdfFile = os.path.join(os.getcwd(), 'samples', 'pdf', '01_simple_text.pdf')
		pdfProcessor = PdfProcessor(samplePdfFile)
		document = pdfProcessor.document()
		expectedDocument = Document().initWithFile(os.path.join(os.getcwd(), 'samples', 'expected outcome', 'docx', 'test_01'))

		self.assertEquals(expectedDocument.content(), document.content())
		self.assertEquals(expectedDocument.formatting(), document.formatting())
