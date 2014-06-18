# -*- coding: UTF-8 -*-

import	os
import	codecs
import	re
from	diff_match_patch	import	diff_match_patch

from	fragments			import	FragmentIdentifier

###############################################################################

class Document:

	def __init__ (self):
		self._analyticIndex = None
		self._properties = None
		self._content = None
		self._formatting = []
		self._metadata = []
		self._sections = None


	def initWithFile (self, documentPath):
		file = codecs.open(os.path.join(documentPath, 'content.txt'), 'r', 'utf-8')
		self._content = []

		for line in file:
			self._content.append(line.rstrip('\n').replace('\\r', '\r'))
		file.close()

		self._formatting	= self.readFragmentFile(os.path.join(documentPath, 'formatting.txt')) or []
		self._metadata		= self.readFragmentFile(os.path.join(documentPath, 'metadata.txt')) or []
		self._properties	= self.readPropertyFile(os.path.join(documentPath, 'properties.txt')) or {}
		return self


	def initWithDocumentInfo (self, content, formatting, metadata, properties=None):
		self._content = content
		if formatting:
			self._formatting = sorted(formatting)
		if metadata:
			self._metadata = sorted(metadata)
		self._properties = properties

		return self


	def readFragmentFile (self, filename):
		if os.path.isfile(filename):
			fragments = []
			file = codecs.open(filename, 'r', 'utf-8')
			for line in file:
				normalizedLine = line.replace('\\n', '\n')
				fragments.append(FragmentIdentifier.fragmentWithLine(normalizedLine, self.content()))
			file.close()
			result = sorted(fragments)
		else:
			result = None

		return result


	def readPropertyFile (self, filename):
		if os.path.isfile(filename):
			pattern = re.compile(r"((?P<spaces>\s+)|(?P<key>[^\s\:][^\:]*)\:)\s*(?P<value>[^\n]+)?", re.DOTALL)
			properties = {}

			file = codecs.open(filename, 'r', 'utf-8')
			key = None
			for line in file:
				match = pattern.match(line)

				if match.group('key'):
					if key:
						properties[key] = value
					key = match.group('key')
					value = match.group('value')
				else:
					if value:
						value += '\n' +  match.group('value')
					else:
						value = match.group('value')
				pass

			if key and value:
				properties[key] = value

			file.close()
			result = properties
		else:
			result = None

		return result

	def content (self):
		return self._content


	def text (self):
		return Document.contentToText(self.content())

	def tableOfContent (self):
		def fragmentTocLevel (fragment):
			if 'style' in fragment.attributes and fragment.attributes['style'].startswith('Heading '):
				result = fragment.attributes['style'][len('Heading '):]
			else:
				result = None
			return result

		rootElement = TocEntry(0, None, 0, None)
		currentElement = rootElement
		count = 0
		for tag in self.tags():
			tagLevel = fragmentTocLevel(tag)
			if tagLevel:
				count += 1
				currentElement = currentElement.addItem(count, tag, tagLevel)

		return rootElement


	def formatting (self):
		return self._formatting

	def metadata (self):
		return self._metadata

	def tags (self):
		return sorted(self.formatting() + self.metadata())


	def writeTo (self, destinationFolder):
		if not os.path.exists(destinationFolder):
			os.makedirs(destinationFolder)

		contentFile = open(os.path.join(destinationFolder, 'content.txt'),	'w')
		for paragraph in self.content():
			contentFile.write(paragraph.replace('\r', '\\r').encode('utf-8') + '\n')
		contentFile.close()

		if self._formatting:
			formattingFile	= open(os.path.join(destinationFolder, 'formatting.txt'),'w')
			for fragment in self._formatting:
				formattingFile.write((unicode(fragment) + '\n').encode('utf-8'))
			formattingFile.close()

		if self._metadata:
			metadataFile	= open(os.path.join(destinationFolder, 'metadata.txt'),'w')
			for fragment in self._metadata:
				metadataFile.write((unicode(fragment) + '\n').encode('utf-8'))
			metadataFile.close()


	def mergeWithDocument (self, newVersion):
		diffs = Document.computeDiffs(self.text(), newVersion.text())
		translationMap = Document.computeTranslationMap(diffs)

		reframedMetadata = []
		for normalizedMetadata in Document.normalizeFragments(self.content(), self.metadata()):
			updatedFragment = normalizedMetadata.updateWithTranslationMap(translationMap)
			if updatedFragment:
				reframedMetadata.append(updatedFragment)

		updatedMetadata = Document.rebaseFragments(newVersion.content(), reframedMetadata)

		return Document().initWithDocumentInfo(newVersion.content(), newVersion.formatting(), updatedMetadata)

	#==========================================================================

	def properties (self):
		if not self._properties:
			self._properties = {}

		return self._properties


	def analyticIndex (self):
		if not self._analyticIndex:
			# TODO: load actual analytic index here
			self._analyticIndex = []

		return self._analyticIndex

	#--------------------------------------------------------------------------

	def sections (self, aSplitFunction):

		def computeSections (aSplitFunction):

			def shouldSplitSectionsAtLine (aSplitFunction, lineNumber):
				result = False

#				fragmentsAtLine = filter(lambda fragment:fragment.shouldSelectionStartAtLine(lineNumber), self.tags())
#				if len(fragmentsAtLine) > 0:
#					result = True
#				else:
#					result = False

				for fragment in filter(lambda fragment:fragment.startingPoint() == (lineNumber, 1), self.tags()):
#					if 'structure' in fragment.attributes and fragment.attributes['structure'] in ['possible-page-break', 'page-break']:
#						result = True
#					if 'style' in fragment.attributes and fragment.attributes['style'].startswith('Heading '):
#						result = True
					if aSplitFunction(fragment):
						result = True

				return result


			result = []
			counter = 1
			fromIndex = 1
			toIndex = 1
			gotSomeActualContent = False
			totalNumberOfLines = len(self.content())

			while toIndex <= totalNumberOfLines:
				if shouldSplitSectionsAtLine(aSplitFunction, toIndex) and gotSomeActualContent:
					result.append(DocumentSection(self, "section_" + str(counter).zfill(2), (fromIndex, toIndex - 1)))
					gotSomeActualContent = False
					counter += 1
					fromIndex = toIndex
				else:
					gotSomeActualContent = True

				toIndex += 1

			result.append(DocumentSection(self, "section_" + str(counter).zfill(2), (fromIndex, toIndex - 1)))

			return result


#		if not self._sections:
#			self._sections = computeSections()
#
#		return self._sections

#		splitFunction = aSplitFunction if aSplitFunction else DocumentSection.splitSectionOnPageBreak
		return computeSections(aSplitFunction)

	#==========================================================================

	@staticmethod
	def normalizeFragments (content, fragments):
		if fragments:
			result = []
			lineAccumulatedCount = Document.lineAccumulatedCount(content)

			for fragment in fragments:
				result.append(fragment.normalize(lineAccumulatedCount[int(fragment.startingPoint()[0]) - 1]))
		else:
			result = None

		return result


	@staticmethod
	def rebaseFragments (content, fragments):
		if fragments:
			result = []
			lineAccumulatedCount = Document.lineAccumulatedCount(content)
			for fragment in fragments:
				result.append(fragment.rebase(lineAccumulatedCount))
		else:
			result = None

		return result


	@staticmethod
	def lineAccumulatedCount (content):
		currentCounter = 0
		result = []
		for line in content:
			result.append((currentCounter, len(line)))
			currentCounter = currentCounter + len(line) + 1

		return result


	@staticmethod
	def computeTranslationMap (diffs):
		result = []
		blockStartIndex = 1
		blockEndIndex = 1
		currentOffset = 0

		for diff in diffs:
			if diff[0] == diff_match_patch.DIFF_EQUAL:
				blockEndIndex = blockStartIndex + len(diff[1])
			elif diff[0] == diff_match_patch.DIFF_INSERT:
				if blockStartIndex < blockEndIndex:
					result.append((blockStartIndex, blockEndIndex, currentOffset))
				blockStartIndex = blockEndIndex
				result.append((blockStartIndex, blockEndIndex, currentOffset, diff[1]))
				currentOffset += len(diff[1])
			elif diff[0] == diff_match_patch.DIFF_DELETE:
				if blockStartIndex < blockEndIndex:
					result.append((blockStartIndex, blockEndIndex, currentOffset))
				blockStartIndex = blockEndIndex + len(diff[1])
				blockEndIndex = blockStartIndex
				currentOffset -= len(diff[1])
			else:
				raise DiffUnhandledCase(diff[0])

		if blockStartIndex < blockEndIndex:
			result.append((blockStartIndex, blockEndIndex, currentOffset))

		return result


	@staticmethod
	def computeDiffs (original, newVersion):
		diffEngine = diff_match_patch()
		result = diffEngine.diff_main(original, newVersion)
		diffEngine.diff_cleanupSemantic(result)

		return result


	@staticmethod
	def contentToText (content):
		return '\n'.join(content) + '\n'


	@staticmethod
	def cleanupTextAndTags (text, tags):
		pass

###############################################################################

class DocumentSection:

	def __init__ (self, document, name, contentRange):
		self._document = document
		self._name = name
		self._contentRange = contentRange

	def document (self):
		return self._document

	def name (self):
		return self._name

	def contentRange (self):
		return self._contentRange

	def content (self):
		return self.document().content()[self.contentRange()[0] - 1:self.contentRange()[1]]

	def isFragmentRelevant (self, fragment):
		return (self.contentRange()[0], 1) <= fragment.startingPoint() < (self.contentRange()[1] + 1, 1)

	def tags (self):
		result = []

		offset = self.contentRange()[0] - 1
		for tag in self.document().tags():
#			if (self.contentRange()[0], 1) <= tag.startingPoint() < (self.contentRange()[1] + 1, 1):
			if self.isFragmentRelevant(tag):
				result.append(tag.shiftFragmentLine(offset, self.contentRange()[1] - self.contentRange()[0] + 1))

		return result

	@staticmethod
	def splitSectionOnPageBreak (fragment):
		return 'structure' in fragment.attributes and fragment.attributes['structure'] in ['possible-page-break', 'page-break']

	@staticmethod
	def splitSectionOnHeaders (fragment):
		return 'style' in fragment.attributes and fragment.attributes['style'].startswith('Heading ')



###############################################################################

class TocEntry:

	def __init__ (self, count, fragment, level, parent):
		self.count = count
		self.fragment = fragment
		self.level = level
		self.parent = parent
		self.children = []

	def addItem (self, count, fragment, level):
		if self.level < level:
			result = TocEntry(count, fragment, level, self)
			self.children.append(result)
		else:
			result = self.parent.addItem(count, fragment, level)

		return result

###############################################################################

class DiffUnhandledCase(Exception):
	pass
