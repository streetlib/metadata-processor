# -*- coding: UTF-8 -*-

import	unittest
from	fragments	import	*

class FragmentsTests (unittest.TestCase):

	def fragment(self, lineNumber, range, text, attributes):
		if range:
			result = LineChunkFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), lineNumber, range, text, attributes)
		else:
			result = WholeLineFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), (lineNumber, lineNumber), text, attributes)

		return result


	def test_fragmentCreation (self):
#		self.assertIsInstance(FragmentIdentifier(),	FragmentIdentifier)
		self.assertIsInstance(self.fragment(0,	None,		"Fist Chapter\n",	{'style':'Heading 1'}),	FragmentIdentifier)
		self.assertIsInstance(self.fragment(1,	(10, 20),	"1234567890",	{}),					FragmentIdentifier)

		self.assertRaises(InvalidFragment, LineChunkFragmentIdentifier().initWithDetails, FragmentIdentifier.getNextIdentifier(), 2, (10, 20), "1234567890123", {})


	def test_fragemntComparison (self):
		a_fragment = self.fragment(1,	(10, 20),	"1234567890",	{})
		b_fragment = self.fragment(1,	(10, 20),	"1234567890",	{})
		self.assertEqual(a_fragment, b_fragment)

		a_fragment = self.fragment(1,	(10, 20),	"1234567890",	{'style': 'Heading 1'})
		b_fragment = self.fragment(1,	(10, 20),	"1234567890",	{'style': 'Heading 1'})
		self.assertEqual(a_fragment, b_fragment)

		a_fragment = self.fragment(1,	(10, 20),	"1234567890",	{'style': 'Heading 1'})
		b_fragment = self.fragment(1,	(10, 20),	"1234567890",	{'style': 'Heading 2'})
		self.assertNotEqual(a_fragment, b_fragment)

		a_fragment = self.fragment(1,	None,		"1234567890\n",	{'style': 'Heading 1'})
		b_fragment = self.fragment(1,	None,		"1234567890\n",	{'style': 'Heading 1'})
		self.assertEqual(a_fragment, b_fragment)


	def test_fragemntDeserializing (self):
#		line = "1:[-] \"I can do that\" - {'style': 'Heading 1'}"
		line = '1: "I can do that\n" - {\'style\': \'Heading 1\'}'
		self.assertEqual(line.replace('\n', '\\n'), str(FragmentIdentifier.fragmentWithLine(line)))


	def test_fragmentSorting (self):
		expectedFragments = [
			self.fragment(1,	None,		"Lorem Ipsum\n",			{'style':'Heading 1'}),
			self.fragment(2,	None,		"Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit...\n",	{'style':'quote'}),
			self.fragment(2,	(1,6),		"Neque",					{'formatting':'italic'}),
			self.fragment(2,	(13,37),	"quisquam est qui dolorem",	{'formatting':'italic'}),
			self.fragment(2,	(13,21),	"quisquam",					{'formatting':'bold'}),
			self.fragment(10,	None,		"Last\n",					{'style':'Heading 1'}),
			self.fragment(11,	(20, 28),	"sentence",					{'formatting':'bold'}),
		]

		fragments = list(expectedFragments)
		fragments.reverse()
		sortedFragments = sorted(fragments)

		self.assertEqual(sortedFragments, expectedFragments)


	def test_fragmentParsing (self):
#		line = '5:[-] "A mia sorella che ha letto le meditazioni\rAlle persone che mi hanno insegnato a meditare e a crescere\rAi miei gatti, piccoli grandi guru" - {\'structure\': \'dedication\'}'
		line = '5: "A mia sorella che ha letto le meditazioni\rAlle persone che mi hanno insegnato a meditare e a crescere\rAi miei gatti, piccoli grandi guru\n" - {\'structure\': \'dedication\'}'
		fragment = FragmentIdentifier.fragmentWithLine(line)
		self.assertIsInstance(fragment, FragmentIdentifier)

		line = '7-9: "Line 1\nLine 2\nLine 3\n" - {\'structure\': \'preface\'}'
		fragment = FragmentIdentifier.fragmentWithLine(line)
		self.assertIsInstance(fragment, FragmentIdentifier)

		line = '7-11: "Line 1\nLine 2\nLine 3\n" - {\'structure\': \'preface\'}'
		self.assertRaises(Exception, FragmentIdentifier.fragmentWithLine, line)


	def test_fragmentDefinitionWithoutText (self):
		content = [
			"Lorem Ipsum",
			"Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit...",
			"Some other text",
			"more random sentences",
			"and more",
			"and more",
			"and more",
			"and more",
			"and more",
			"Last",
			"paragraph with the sentence placed here just to fulfill test expectations"
		]

		fragments = [
			FragmentIdentifier.fragmentWithLine("1: - {'style':'Heading 1'}", content),
			FragmentIdentifier.fragmentWithLine("2: - {'style':'quote'}", content),
			FragmentIdentifier.fragmentWithLine("2:[1-6] - {'formatting':'italic'}", content),
			FragmentIdentifier.fragmentWithLine("2:[13-37] - {'formatting':'italic'}", content),
			FragmentIdentifier.fragmentWithLine("2:[13-21] - {'formatting':'bold'}", content),
			FragmentIdentifier.fragmentWithLine("5-9: - {'style':'boring'}", content),
			FragmentIdentifier.fragmentWithLine("10: - {'style':'Heading 1'}", content),
			FragmentIdentifier.fragmentWithLine("11:[20-28] - {'formatting':'bold'}", content)
		]

		expectedFragments = [
			self.fragment(1,	None,		"Lorem Ipsum\n",			{'style':'Heading 1'}),
			self.fragment(2,	None,		"Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit...\n",	{'style':'quote'}),
			self.fragment(2,	(1,6),		"Neque",					{'formatting':'italic'}),
			self.fragment(2,	(13,37),	"quisquam est qui dolorem",	{'formatting':'italic'}),
			self.fragment(2,	(13,21),	"quisquam",					{'formatting':'bold'}),
			WholeLineFragmentIdentifier().initWithDetails(FragmentIdentifier.getNextIdentifier(), (5,9), "and more\nand more\nand more\nand more\nand more\n", {'style':'boring'}),
			self.fragment(10,	None,		"Last\n",					{'style':'Heading 1'}),
			self.fragment(11,	(20, 28),	"sentence",					{'formatting':'bold'}),
		]

		self.assertEqual(fragments, expectedFragments)


	def test_fragmentLines (self):
		content = [
			"Line  1",
			"Line  2",
			"Line  3",
			"Line  4",
			"Line  5",
			"Line  6",
			"Line  7",
			"Line  8",
			"Line  9",
			"Line 10",
		]

		fragment = FragmentIdentifier.fragmentWithLine("1: - {}", content)
		self.assertEqual(1, len(fragment.contentLines()))
		self.assertEqual("Line  1", fragment.lastLine())

		fragment = FragmentIdentifier.fragmentWithLine("1-4: - {}", content)
		self.assertEqual(4, len(fragment.contentLines()))
		self.assertEqual("Line  4", fragment.lastLine())

		fragment = FragmentIdentifier.fragmentWithLine("3-7: - {}", content)
		self.assertEqual(5, len(fragment.contentLines()))
		self.assertEqual("Line  7", fragment.lastLine())

		fragment = FragmentIdentifier.fragmentWithLine("10: - {}", content)
		self.assertEqual(1, len(fragment.contentLines()))
		self.assertEqual("Line 10", fragment.lastLine())

