# -*- coding: UTF-8 -*-

import	unittest
from	fragments	import	*
from	document	import	*

class DocumentSectionTests (unittest.TestCase):

	def test_singleSection (self):
		content = [
			"intro",
			"line 2",
			"line 3"
		]
		document = Document().initWithDocumentInfo(content, [], [])
		sections = document.sections(DocumentSection.splitSectionOnHeaders)
		self.assertEquals(1, len(sections))
		self.assertEquals(content, sections[0].content())

	def test_introAndChapter (self):
		content = [
			"intro",
			"# Chapter 1",
			"content of",
			"chapter 1"
		]
		document = Document().initWithDocumentInfo(content, [], [
			FragmentIdentifier.fragmentWithLine("2: - {'style': 'Heading 1'}", content)
		])

		sections = document.sections(DocumentSection.splitSectionOnHeaders)
		self.assertEquals(2, len(sections))
		self.assertEquals(["intro"], sections[0].content())
		self.assertEquals(["# Chapter 1", "content of", "chapter 1"], sections[1].content())


	def test_introAndMultipleChapters (self):
		content = [
			"intro",
			"# Chapter 1",
			"content of",
			"chapter 1",
			"# Chapter 2",
			"some content of chapter 2",
			"# Chapter 3",
			"more content for",
			"chapter 3",
			"and an extra line here"
		]
		document = Document().initWithDocumentInfo(content, [], [
			FragmentIdentifier.fragmentWithLine("2: - {'style': 'Heading 1'}", content),
			FragmentIdentifier.fragmentWithLine("5: - {'style': 'Heading 1'}", content),
			FragmentIdentifier.fragmentWithLine("7: - {'style': 'Heading 1'}", content)
		])
		sections = document.sections(DocumentSection.splitSectionOnHeaders)
		self.assertEquals(4, len(sections))
		self.assertEquals(["intro"], sections[0].content())
		self.assertEquals(["# Chapter 1", "content of", "chapter 1"], sections[1].content())
		self.assertEquals(["# Chapter 2", "some content of chapter 2"], sections[2].content())
		self.assertEquals(["# Chapter 3", "more content for", "chapter 3", "and an extra line here"], sections[3].content())


	def test_introAndMultipleChaptersAndSubchapters (self):
		content = [
			"intro",
			"# Chapter 1",
			"## Subchapter 1.1",
			"content of subchapter 1.1",
			"## Subchapter 1.2",
			"content of subchapter 1.2",
			"with some extra content",
			"# Chapter 2",
			"some content of chapter 2",
			"# Chapter 3",
			"## Subchapter 3.1",
			"content for subchapter 3.1",
			"and an extra line here",
			"and some more",
			"## Subchapter 3.2",
			"content for subchapter 3.2",
			"## Subchapter 3.3",
			"content for subchapter 3.3",
			"and some extra content here"
		]
		document = Document().initWithDocumentInfo(content, [], [
			FragmentIdentifier.fragmentWithLine("2: - {'style': 'Heading 1'}", content),
			FragmentIdentifier.fragmentWithLine("3: - {'style': 'Heading 2'}", content),
			FragmentIdentifier.fragmentWithLine("4:[12-26] - {'formattings': ['bold']}", content),
			FragmentIdentifier.fragmentWithLine("5: - {'style': 'Heading 2'}", content),
			FragmentIdentifier.fragmentWithLine("8: - {'style': 'Heading 1'}", content),
			FragmentIdentifier.fragmentWithLine("10: - {'style': 'Heading 1'}", content),
			FragmentIdentifier.fragmentWithLine("11: - {'style': 'Heading 2'}", content),
			FragmentIdentifier.fragmentWithLine("15: - {'style': 'Heading 2'}", content),
			FragmentIdentifier.fragmentWithLine("17: - {'style': 'Heading 2'}", content),
		])

		sections = document.sections(DocumentSection.splitSectionOnHeaders)
		self.assertEquals(7, len(sections))

		self.assertEquals(( 1,  1), sections[0].contentRange())
		self.assertEquals(( 2,  4), sections[1].contentRange())
		self.assertEquals(( 5,  7), sections[2].contentRange())
		self.assertEquals(( 8,  9), sections[3].contentRange())
		self.assertEquals((10, 14), sections[4].contentRange())
		self.assertEquals((15, 16), sections[5].contentRange())
		self.assertEquals((17, 19), sections[6].contentRange())


		self.assertEquals(["intro"], sections[0].content())
		self.assertEquals(["# Chapter 1", "## Subchapter 1.1", "content of subchapter 1.1"], sections[1].content())
		self.assertEquals(["## Subchapter 1.2", "content of subchapter 1.2", "with some extra content"], sections[2].content())
		self.assertEquals(["# Chapter 2", "some content of chapter 2"], sections[3].content())
		self.assertEquals(["# Chapter 3", "## Subchapter 3.1", "content for subchapter 3.1", "and an extra line here", "and some more"], sections[4].content())
		self.assertEquals(["## Subchapter 3.2", "content for subchapter 3.2"], sections[5].content())
		self.assertEquals(["## Subchapter 3.3", "content for subchapter 3.3", "and some extra content here"], sections[6].content())

		self.assertEquals(3, len(sections[1].tags()))
		self.assertEquals(1, len(sections[2].tags()))
		self.assertEquals("1: \"# Chapter 3\\n\" - {'style': 'Heading 1'}", str(sections[4].tags()[0]))
		self.assertEquals("2: \"## Subchapter 3.1\\n\" - {'style': 'Heading 2'}", str(sections[4].tags()[1]))
