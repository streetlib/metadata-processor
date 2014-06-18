# -*- coding: UTF-8 -*-

import	unittest
from	fragments	import	*
from	document	import	*

class DocumentTOCTests (unittest.TestCase):

	def test_singleSection (self):
 		document = Document().initWithFile(os.path.join(os.getcwd(), 'samples', 'expected outcome', 'docx', 'test_03'))
		toc = document.tableOfContent()
 		self.assertEquals(5, len(toc.children))
 		self.assertEquals('I can do that\n', toc.children[0].fragment.text)
 		self.assertEquals('I gotta piss\n', toc.children[1].fragment.text)


	def test_singleTOC (self):
	#	Section 1
	#		First Chapter
	#		Second Chapter
	#	Section 2
	#       Third Chapter
	#			Subchapter a
	#			Subchapter b
	#		Fourth Chapter

		document = Document().initWithFile(os.path.join(os.getcwd(), 'samples', 'expected outcome', 'docx', 'test_09'))
		toc = document.tableOfContent()
		self.assertEquals(2, len(toc.children))

		section1 = toc.children[0]
		self.assertEquals("First Chapter\n", section1.children[0].fragment.text)

		section2 = toc.children[1]
		chapter3 = section2.children[0]
		self.assertEquals("Subchapter b\n", chapter3.children[1].fragment.text)
		self.assertEquals(7, chapter3.children[1].count)
