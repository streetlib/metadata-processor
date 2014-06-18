# -*- coding: UTF-8 -*-

import	unittest
import	os
import	filecmp

from	document	import	Document
from	fragments	import 	FragmentIdentifier
from	ePub		import	ePubGenerator

class ePubTests (unittest.TestCase):

	def test_simpleContentSerializedAsXHTM (self):
		content = [
			"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
		]
		tags = [
			FragmentIdentifier.fragmentWithLine("1:[1-12] - {'formattings':['bold']}", content, '1'),
		]

		result = ePubGenerator.renderContentAsXHTML(content, tags)
		expectedResult = '<p><b id="1">Lorem ipsum</b> dolor sit amet, consectetur adipiscing elit.</p>\n'
		self.assertEqual(expectedResult, result)


	def test_contentSerializedAsXHTM (self):
		content = [
			"Chapter 1",
			"Paragraph 1.",
		]
		tags = []

		result = ePubGenerator.renderContentAsXHTML(content, tags)
		expectedResult =\
"""\
<p>Chapter 1</p>
<p>Paragraph 1.</p>
"""
		self.assertEqual(expectedResult, result)


	def test_contentSerializedAsXHTM_2 (self):
		content = [
			"Chapter 1",
			"Paragraph 1.",
		]
		tags = [
			FragmentIdentifier.fragmentWithLine("1: - {'style':'Heading 1'}", content, '1'),
		]

		result = ePubGenerator.renderContentAsXHTML(content, tags)
		expectedResult = \
"""\
<h1 id="1">Chapter 1</h1>
<p>Paragraph 1.</p>
"""
		self.assertEqual(expectedResult, result)


	def test_contentSerializedAsXHTM_3 (self):
		content = [
			"Chapter 1",
			"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
			"Cras sed velit odio, at gravida lectus. Donec sed ligula in est dictum lacinia.",
			"Cras id sem placerat libero facilisis sagittis ac ut elit."
		]
		tags = [
			FragmentIdentifier.fragmentWithLine("1: - {'style':'Heading 1'}", content, '1'),
			FragmentIdentifier.fragmentWithLine("2:[1-12] - {'formattings':['bold']}", content, '2'),
			FragmentIdentifier.fragmentWithLine("3:[25-39] - {'formattings':['italic']}", content, '3'),
			FragmentIdentifier.fragmentWithLine("4:[29-47] - {'formattings':['underline']}", content, '4'),
		]

		result = ePubGenerator.renderContentAsXHTML(content, tags)
		expectedResult =\
"""\
<h1 id="1">Chapter 1</h1>
<p><b id="2">Lorem ipsum</b> dolor sit amet, consectetur adipiscing elit.</p>
<p>Cras sed velit odio, at <i id="3">gravida lectus</i>. Donec sed ligula in est dictum lacinia.</p>
<p>Cras id sem placerat libero <span id="4" class="underline">facilisis sagittis</span> ac ut elit.</p>
"""
		self.assertEqual(expectedResult, result)


	def test_contentSerializedAsXHTM_4 (self):
		content = [
			"Chapter 1",
			"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
			"Cras sed velit odio, at gravida lectus. Donec sed ligula in est dictum lacinia.",
			"Cras id sem placerat libero facilisis sagittis ac ut elit."
		]
		tags = [
			FragmentIdentifier.fragmentWithLine("1-4: - {'structure':'line-block'}", content, '1'),
			FragmentIdentifier.fragmentWithLine("1: - {'style':'Heading 1'}", content, '2'),
			FragmentIdentifier.fragmentWithLine("2:[1-12] - {'formattings':['bold']}", content, '3'),
			FragmentIdentifier.fragmentWithLine("3:[25-39] - {'formattings':['italic']}", content, '4'),
			FragmentIdentifier.fragmentWithLine("4:[29-47] - {'formattings':['underline']}", content, '5'),
			]

		result = ePubGenerator.renderContentAsXHTML(content, tags)
		expectedResult = \
"""\
<div id="1" class="line-block"><h1 id="2">Chapter 1</h1>
<p><b id="3">Lorem ipsum</b> dolor sit amet, consectetur adipiscing elit.</p>
<p>Cras sed velit odio, at <i id="4">gravida lectus</i>. Donec sed ligula in est dictum lacinia.</p>
<p>Cras id sem placerat libero <span id="5" class="underline">facilisis sagittis</span> ac ut elit.</p></div>
"""
		self.assertEqual(expectedResult, result)


	def test_contentSerializedAsXHTM_overlappingTags (self):
		content = [
			"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
			#+---- bold -----+
			#      +-- italic ---+
			#            + underline -+

		]
		tags = [
			FragmentIdentifier.fragmentWithLine("1:[1-18] - {'formattings':['bold']}", content, '1'),
			FragmentIdentifier.fragmentWithLine("1:[7-22] - {'formattings':['italic']}", content, '2'),
			FragmentIdentifier.fragmentWithLine("1:[13-27] - {'formattings':['underline']}", content, '3'),
		]

		result = ePubGenerator.renderContentAsXHTML(content, tags)
		expectedResult = """<p><b id="1">Lorem <i id="2">ipsum <span id="3" class="underline">dolor</span></i></b><i><span class="underline"> sit</span></i><span class="underline"> amet</span>, consectetur adipiscing elit.</p>\n"""
		self.assertEqual(expectedResult, result)


	def test_contentSerializedAsXHTM_overlappingTags_2 (self):
		content = [
			"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
			#+---- bold -----+
			#      +-- italic ---+
			#            + underline -+
			#                                        +- bold -+

		]
		tags = [
			FragmentIdentifier.fragmentWithLine("1:[1-18] - {'formattings':['bold']}", content, '1'),
			FragmentIdentifier.fragmentWithLine("1:[7-22] - {'formattings':['italic']}", content, '2'),
			FragmentIdentifier.fragmentWithLine("1:[13-27] - {'formattings':['underline']}", content, '3'),
			FragmentIdentifier.fragmentWithLine("1:[41-51] - {'formattings':['bold']}", content, '4'),
		]

		result = ePubGenerator.renderContentAsXHTML(content, tags)
		expectedResult = """<p><b id="1">Lorem <i id="2">ipsum <span id="3" class="underline">dolor</span></i></b><i><span class="underline"> sit</span></i><span class="underline"> amet</span>, consectetur <b id="4">adipiscing</b> elit.</p>\n"""
		self.assertEqual(expectedResult, result)


	def test_breakLineRendering (self):
		content = [
			"""Lorem ipsum dolor sit amet,\\rconsectetur adipiscing elit.""",
		]
		result = ePubGenerator.renderContentAsXHTML(content, [])
		expectedResult = """<p>Lorem ipsum dolor sit amet,<br />consectetur adipiscing elit.</p>\n"""
		self.assertEqual(expectedResult, result)
