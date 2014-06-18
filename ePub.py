# -*- coding: UTF-8 -*-

import	os
import	string
import	codecs
import	zipfile
import	zlib
import	codecs

from	lxml		import	etree
from	lxml		import	html
from	document	import	Document
from	document	import	DocumentSection
from	fragments	import	*

###############################################################################

DC_NAMESPACE	= 'http://purl.org/dc/elements/1.1/'
XLINK_NAMESPACE	= 'http://www.w3.org/1999/xlink'
OPF_NAMESPACE	= 'http://www.idpf.org/2007/opf'
XML_NAMESPACE	= 'http://www.w3.org/XML/1998/namespace'

NAMESPACES = {
	'dc':    DC_NAMESPACE,
	'xlink': XLINK_NAMESPACE,
	'opf':   OPF_NAMESPACE,
	'xml':   XML_NAMESPACE
}

# UNICODE_LINE_SEPARATOR		= u'\u2028'
# UNICODE_PARAGRAPH_SEPARATOR	= u'\u2029'

class ePubGenerator:

	def generateEPubFromDocument (self, document, ePubTargetFile, aTemplateName):
		self._templateName = aTemplateName

		ePubDocument = ePub()

		for property in document.properties().items():
			ePubDocument.setProperty(*property)

		sections = document.sections(DocumentSection.splitSectionOnPageBreak)
		ePubDocument.addResource(ePubResource("stylesheet.css", 'text/css', self.stylesheet()))
		ePubDocument.addResource(ePubResource("cover.html", 'application/xhtml+xml', self.coverForDocument(document)), True)
		ePubDocument.addResource(ePubResource("toc.ncx", 'application/x-dtbncx+xml', ePubDocument.toc_ncx(sections, document.tableOfContent())))

		for section in sections:
			sectionResource = ePubResource(section.name() + '.html', 'application/xhtml+xml', self.xhtmlContentForSection(section))
			ePubDocument.addResource(sectionResource, True)

		analyticIndex = document.analyticIndex()
		if analyticIndex:
			ncxAnalyticIndex = self.transformAnalyticIndex(analyticIndex)
#			ePubDocument.addResource(ePubResource("toc.ncx", 'application/x-dtbncx+xml', ncxAnalyticIndex))

		ePubDocument.writeTo(ePubTargetFile)


	def templateName (self):
		return self._templateName


	def stylesheet (self):
		return open(os.path.join(os.getcwd(), 'resources', 'templates', self.templateName(), 'stylesheet.css')).read().decode('utf8')

	def coverForDocument (self, document):
		title = document.properties()['title']
		author = document.properties()['creator']
		language = document.properties()['language']

		html = etree.Element('html', {'xmlns':'http://www.w3.org/1999/xhtml', '{%s}lang'%XML_NAMESPACE:language}, NAMESPACES)
		head = etree.SubElement(html, 'head')
		etree.SubElement(head, 'title').text = title
		etree.SubElement(head, 'link', {'href':'../Styles/stylesheet.css', 'rel':'stylesheet', 'type':'text/css'})

		body = etree.SubElement(html, 'body', {'class':'cover'})
		etree.SubElement(body, 'h1', {'class':'title'}).text = title
		etree.SubElement(body, 'h3', {'class':'author'}).text = author

		result = etree.tostring(
			etree.ElementTree(html),
			xml_declaration=True,
			encoding='utf-8',
			standalone=False,
			doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">"
		)
		return result


	def xhtmlContentForSection (self, section):
		title = section.document().properties()['title']
		language = section.document().properties()['language']

		document = etree.Element('html', {'xmlns':'http://www.w3.org/1999/xhtml', '{%s}lang'%XML_NAMESPACE:language}, NAMESPACES)
		head = etree.SubElement(document, 'head')
		etree.SubElement(head, 'title').text = title
		etree.SubElement(head, 'link', {'href':'../Styles/stylesheet.css', 'rel':'stylesheet', 'type':'text/css'})

		content = ePubGenerator.renderContentAsXHTML(section.content(), section.tags())
		body = html.fragment_fromstring(content, 'body')
		body.set('class', 'section')
		document.append(body)

		result = etree.tostring(
			etree.ElementTree(document),
			xml_declaration=True,
			encoding='utf-8',
			standalone=False,
			doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">"
		)

		return result


	#==========================================================================

	@staticmethod
	def renderContentAsXHTML (content, tags):

		def contentFromTo (content, fromPosition, toPosition):
			result = ''
			if fromPosition < toPosition:
				position = fromPosition
				while position[0] < toPosition[0]:
					result += content[position[0] - 1][position[1] -1:] + '\n'
#					result += content[position[0] - 1][position[1] -1:] + UNICODE_LINE_SEPARATOR
					position = (position[0] + 1, 1)

				result += content[position[0] - 1][position[1] - 1 :toPosition[1] - 1]

#			if u'sce da me ed è me.' in result:
#				raise Exception("WTF")

			return result.replace('\\r', '<br />')

		def tagForFormatting (formatting):
			if formatting == 'bold':
				result = ('b', None)
			elif formatting == 'italic':
				result = ('i', None)
			elif formatting == 'underline':
				result = ("span", ['class="underline"'])
			else:
				raise Exception("unrecognized formatting: " + formatting)
			return result

		def tagForStyle (style):
			if style == 'Heading 1':
				result = ('h1', None)
			elif style == 'Heading 2':
				result = ('h2', None)
			else:
				raise Exception("unrecognized style: " + style)
			return result

		def tagForStructure (structure, isWholeLine):
			if structure == 'paragraph':
				result = ('p', None)
			else:
				if isWholeLine:
					result = ('div',  ['class="' + structure + '"'])
				else:
					result = ('span', ['class="' + structure + '"'])
			return result

		def tagsForFormattingsAndStyle (fragment):
			result = []

			if 'structure' in fragment.attributes:
				result.append(tagForStructure(fragment.attributes['structure'], fragment.isWholeLine()))
			if 'formattings' in fragment.attributes:
				for formatting in sorted(fragment.attributes['formattings']):
					result.append(tagForFormatting(formatting))
			if 'style' in fragment.attributes:
				result.append(tagForStyle(fragment.attributes['style']))

			return result

		def openTagForFragment (fragment, isFirstOpening=False):
			for tag in tagsForFormattingsAndStyle(fragment):
				result = '<' + tag[0]
				if fragment.identifier and isFirstOpening:
					result += ' id="' + fragment.identifier + '"'
				if tag[1]:
					for attribute in tag[1]:
						result += " " + attribute
				result += '>'
#			if 'structure' in fragment.attributes:
#				result += '<div class="' + fragment.attributes['structure'] + '">'
			return result

		def closeTagForFragment (fragment):
			for tag in tagsForFormattingsAndStyle(fragment):
				result = '</' + tag[0] + '>'
#			if 'structure' in fragment.attributes:
#				result += '</div>'
			return result


		def openFragment (result, content, index, fragment):
			updatedResult = result + \
							contentFromTo(content, index, fragment.startingPoint()) + \
							openTagForFragment(fragment, True)
			updatedIndex = fragment.startingPoint()
			return (updatedResult, updatedIndex)

		def closeFragments (result, content, index, fragments):
			updatedResult = result
			updatedIndex = index

			for fragmentToClose in fragments:
				updatedResult, updatedIndex = closeFragment(updatedResult, content, updatedIndex, fragmentToClose, fragments)
				pendingTags.remove(fragmentToClose)

			return updatedResult, updatedIndex

		def closeFragment (result, content, index, fragment, openFragments):
			updatedResult = result + contentFromTo(content, index, fragment.endingPoint())
			updatedIndex = fragment.endingPoint()

			nestedFragments = sorted(filter(lambda openFragment:fragment.startingPoint() < openFragment.startingPoint() and fragment.endingPoint() < openFragment.endingPoint(), openFragments), reverse=True)
			for nestedFragment in nestedFragments:
				updatedResult += closeTagForFragment(nestedFragment)

			updatedResult += closeTagForFragment(fragment)

			for nestedFragment in sorted(nestedFragments):
				updatedResult += openTagForFragment(nestedFragment)

			return (updatedResult, updatedIndex)


		def sortedPendingTags (fragments):
			def compareFragmentEnding(fragment1, fragment2):
				if fragment1.endingPoint() < fragment2.endingPoint():
					result = -1
				elif fragment1.endingPoint() > fragment2.endingPoint():
					result = 1
				else:
					if fragment1.startingPoint() > fragment2.startingPoint():
						result = -1
					elif fragment1.startingPoint() < fragment2.startingPoint():
						result = 1
					else:
						result = 0

				return result

#			return sorted(fragments, key=lambda fragment: fragment.endingPoint())
			return sorted(fragments, cmp=compareFragmentEnding)

		def fragmentToCloseBefore (fragments, nextStartingPoint):
			result = []
			for fragment in sortedPendingTags(fragments):
				if fragment.endingPoint() <= nextStartingPoint:
					result.append(fragment)
			return result

		#----------------------------------------------------------------------

		result = ''
		index = (1, 1)
		pendingTags = []

		extendedFragments = list(tags)

		for i in range(len(content)):
			def alreadyExistsAWholeParagraphStyle (lineNumber):
				result = False
				for fragment in tags:
					if fragment.isWholeLine()\
					and fragment.lineRange == (lineNumber, lineNumber)\
					and 'style' in fragment.attributes:
						result = True
				return result

			if not alreadyExistsAWholeParagraphStyle (i+1):
				extendedFragments.append(WholeLineFragmentIdentifier().initWithDetails(None, (i+1, i+1), content[i] + '\n', {'structure': 'paragraph'}))

		for fragment in sorted(extendedFragments):
			result, index = closeFragments(result, content, index, fragmentToCloseBefore(pendingTags, fragment.startingPoint()))
			result, index = openFragment(result, content, index, fragment)
			pendingTags.append(fragment)

		result, index = closeFragments(result, content, index, sortedPendingTags(pendingTags))

		result += contentFromTo(content, index, (len(content), len(content[-1]) + 1)) + '\n'
		return result

###############################################################################

class ePub:
	def __init__ (self):
		self._properties= {}
		self._resources	= {}
		self._spine		= []
#		self._guide		= None


	def properties (self):
		return self._properties

	def setProperty (self, propertyName, propertyValue):
		self._properties[propertyName] = propertyValue


	def resources (self):
		return self._resources

	def spine (self):
		return self._spine

	def addResource (self, resource, addToSpine=False):
		resource.setEPub(self)
		self._resources[resource.name()] = resource
		if addToSpine:
			self._spine.append(resource)


	def writeTo (self, targetFile):
		ePubFile = zipfile.ZipFile(targetFile, mode='w', compression=zipfile.ZIP_STORED)
		ePubFile.writestr('mimetype', 'application/epub+zip')
		ePubFile.writestr('META-INF/container.xml',	self.containerFile())
		ePubFile.writestr('OEBPS/content.opf',		self.content_opf())
		for resource in self.resources().values():
			ePubFile.writestr(os.path.join('OEBPS', resource.path()), resource.content())
		ePubFile.close()

	#--------------------------------------------------------------------------

	def containerFile (self):
		container = etree.Element('container', {'version':'1.0', 'xmlns':'urn:oasis:names:tc:opendocument:xmlns:container'})
		rootFiles = etree.SubElement(container, 'rootfiles')
		rootFile  = etree.SubElement(rootFiles, 'rootfile', {'full-path':'OEBPS/content.opf', 'media-type':'application/oebps-package+xml'})

		result = etree.tostring(etree.ElementTree(container), xml_declaration=True, encoding='UTF-8', standalone=False)
		return result

	#..........................................................................

	def content_opf (self):
		propertyItems = dict(self.properties())

		isbn = propertyItems['isbn']
		del propertyItems['isbn']

		package = etree.Element('package', {
			'unique-identifier': 'isbn' + isbn,
			'version': '2.0',
			'xmlns': 'http://www.idpf.org/2007/opf',
		})
		metadata = etree.SubElement(package, 'metadata', None, NAMESPACES)
		etree.SubElement(metadata, '{%s}identifier'%DC_NAMESPACE, {
			'id': 'isbn' + isbn,
			'{%s}scheme'%OPF_NAMESPACE: 'ISBN'
		}).text = isbn
		for property in propertyItems.items():
			etree.SubElement(metadata, '{%s}%s' % (DC_NAMESPACE, property[0])).text = property[1]

		manifest = etree.SubElement(package, 'manifest')
		for resource in self.resources().values():
			etree.SubElement(manifest, 'item', {
				'id': resource.id(),
				'href': resource.href(),
				'media-type': resource.mediaType()
			})

		spine = etree.SubElement(package, 'spine', {'toc':'toc'})
		for resource in self.spine():
			etree.SubElement(spine, 'itemref', {'idref':resource.idref()})

		result = etree.tostring(etree.ElementTree(package), xml_declaration=True, encoding='utf-8', standalone=True)
		return result

	#..........................................................................

	def toc_ncx (self, sections, tableOfContent):

		def fragmentUrl (fragment):
			section = filter(lambda i:i.isFragmentRelevant(fragment), sections)[0]
			result = 'Text/' + section.name() + '.html#' + fragment.identifier

			return result

		def appendNavPoints (element, tocEntries):
			for tocEntry in tocEntries:
				navPoint = etree.SubElement(element, 'navPoint', {'id': 'navpoint-' + str(tocEntry.count), 'playOrder': str(tocEntry.count)})
				navLabel = etree.SubElement(navPoint, 'navLabel')
				navLabelText = etree.SubElement(navLabel, 'text').text = tocEntry.fragment.text[:-1]
				content = etree.SubElement(navPoint, 'content', {'src': fragmentUrl(tocEntry.fragment)})
				appendNavPoints(navPoint, tocEntry.children)


		ncx = etree.Element('ncx', {
			'version': '2005-1',
			'{%s}%s'%(XML_NAMESPACE, 'lang'): self.properties()['language'],
			'xmlns': 'http://www.daisy.org/z3986/2005/ncx/',
		})
		head = etree.SubElement(ncx, 'head')
		meta = etree.SubElement(head, 'meta', {
			'name': 'dtb:uid',
			'content': self.properties()['isbn'],
		})

		docTitle = etree.SubElement(ncx, 'docTitle')
		etree.SubElement(docTitle, 'text').text = self.properties()['title']

		navMap = etree.SubElement(ncx, 'navMap')
		appendNavPoints(navMap, tableOfContent.children)

		result = etree.tostring(
			etree.ElementTree(ncx),
			xml_declaration=True,
			encoding='utf-8',
			standalone=False,
			doctype="<!DOCTYPE ncx PUBLIC \"-//NISO//DTD ncx 2005-1//EN\" \"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd\">"
		)
		return result

###############################################################################

class ePubResource:

	def __init__ (self, name, mediaType, content):
		self._name = name
		self._mediaType = mediaType
		self._content = content

		self._ePub = None
		self._id = None

	def name (self):
		return self._name

	def content (self):
		return self._content

	def mediaType (self):
		return self._mediaType

	def ePub (self):
		return self._ePub

	def setEPub (self, ePub):
		self._ePub = ePub

	#--------------------------------------------------------------------------

	def id (self):
		if not self._id:
			self._id = os.path.splitext(self.name())[0]

		return self._id

	def path (self):
		if self.mediaType() == 'text/css':
			result = 'Styles'
		elif self.mediaType() == 'application/xhtml+xml':
			result = 'Text'
#		elif self.mediaType() == 'application/x-dtbncx+xml':
#			result = ''
		else:
			result = ''

		result = os.path.join(result, self.name())
		return result

	def href (self):
		return self.path()

	def idref (self):
		return self.id()

###############################################################################
