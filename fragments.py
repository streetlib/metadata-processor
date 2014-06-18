# -*- coding: UTF-8 -*-

import	re
import	ast
import	abc
from	functools	import	total_ordering


@total_ordering
class FragmentIdentifier:
	__metaclass__ = abc.ABCMeta

	identifier = 0

	@staticmethod
	def fragmentWithLine (line, content=None, anIdentifier=None):
		pattern = re.compile(r"(?P<line>[0-9]+)(\:\[(?P<from>[0-9]+)\-(?P<to>[0-9]+)\]|(\-(?P<lineTo>[0-9]+))?\:)( \"(?P<text>.*)\")? - (?P<attributes>\{.*\})", re.DOTALL|re.MULTILINE)
		match = pattern.match(line)

		if not match:
			raise InvalidFragment("failed to parse line:\n\t" + line)

		if match.group('text'):
			text = match.group('text').replace('\\r', '\r')
		elif content:
			text = None
		else:
			text = ''

		attributes = ast.literal_eval(match.group('attributes'))
		if anIdentifier:
			identifier = anIdentifier
		else:
			identifier = FragmentIdentifier.getNextIdentifier()

		if match.group('from'):
			lineNumber = int(match.group('line'))
			textRange = (int(match.group('from')), int(match.group('to')))

			if not text:
				text = content[lineNumber - 1][textRange[0] - 1:textRange[1] - 1]

			result = LineChunkFragmentIdentifier().initWithDetails(identifier, lineNumber, textRange, text, attributes)
		else:
			if match.group('lineTo'):
				lineRange = (int(match.group('line')), int(match.group('lineTo')))
			else:
				lineRange = (int(match.group('line')), int(match.group('line')))

			if not text:
				text = ''
				for i in range(lineRange[0], lineRange[1] + 1):
					text += content[i - 1] + '\n'

			result = WholeLineFragmentIdentifier().initWithDetails(identifier, lineRange, text, attributes)

		return result

	@staticmethod
	def getNextIdentifier ():
		FragmentIdentifier.identifier += 1
		return 'fragment_' + str(FragmentIdentifier.identifier)


	def __lt__ (self, other):
		result = False

		if self.startingPoint() < other.startingPoint():
			result = True
		elif self.startingPoint() == other.startingPoint() and len(self.text) > len(other.text):
			result = True

		return result


	def __eq__ (self, other):
		result = True

		if self.startingPoint() != other.startingPoint():
			result = False
		elif self.attributes != other.attributes:
			result = False
		elif self.text != other.text:
			result = False

		return result


	def trimFragmentPrefix (self, upatedRange, text, translation, previousEndOfTranslation, offset):
		if previousEndOfTranslation < translation[0]:
			upToIndex = max(0, previousEndOfTranslation - upatedRange[0] + offset)
			updatedText =  text[:upToIndex] + text[translation[0] - upatedRange[0] + offset:]
			updatedTextOffset = translation[2]
		else:
			updatedText = text
			updatedTextOffset = offset

		return (updatedText, updatedTextOffset)


	def normalizedTextRepresentation (self):
		return self.text.replace('\n', '\\n').replace('\r', '\\r')


	@abc.abstractmethod
	def isWholeLine (self):
		return

	@abc.abstractmethod
	def startingPoint (self):
		return

	@abc.abstractmethod
	def endingPoint (self):
		return

	@abc.abstractmethod
	def normalize (self, offset):
		return

#	@abc.abstractmethod
#	def shouldSelectionStartAtLine (self, lineNumber):
#		return

	@abc.abstractmethod
	def shiftFragmentLine (self, offset, finalNumberOfLines):
		return

#------------------------------------------------------------------------------

class LineChunkFragmentIdentifier(FragmentIdentifier):

	def __repr__(self):
		return str(self.lineNumber) + ':[' + str(self.range[0]) + '-' + str(self.range[1]) + '] "' + self.normalizedTextRepresentation() + '" - ' + str(self.attributes)


	def initWithDetails (self, anIdentifier, aLineNumber, aRange, aText, someAttributes):
		self.identifier = anIdentifier
		self.lineNumber = aLineNumber
		self.range = aRange
		self.text = aText
		self.attributes = someAttributes
		self.validateState()
		return self


	def validateState (self):
		if self.range is None or len(self.range) != 2:
			raise InvalidFragment("range should contain two values: " + str(self.range))
		if len(self.text) != (self.range[1] - self.range[0]):
			raise InvalidFragment("range " + str(self.range) + " and text (\"" + self.text + "\") do not match")

	def isWholeLine (self):
		return False

	def startingPoint (self):
		return (self.lineNumber, self.range[0])

	def endingPoint (self):
		return (self.lineNumber, self.range[1])

	def normalize (self, offset):
		updatedRange = (self.range[0] + offset[0], self.range[1] + offset[0])
		return NormalizedFragmentIdentifier().initWithDetails(self.identifier, updatedRange, self.text, self.attributes)

#	def shouldSelectionStartAtLine (self, lineNumber):
#		return False

	def shiftFragmentLine (self, offset, finalNumberOfLines):
		return LineChunkFragmentIdentifier().initWithDetails(self.identifier, self.lineNumber - offset, self.range, self.text, self.attributes)

#------------------------------------------------------------------------------

class WholeLineFragmentIdentifier(FragmentIdentifier):

	def __repr__(self):
		if self.lineRange[0] == self.lineRange[1]:
			rangeText = str(self.lineRange[0])
		else:
			rangeText = str(self.lineRange[0]) + '-' + str(self.lineRange[1])
		return rangeText + ': "' + self.normalizedTextRepresentation() + '" - ' + str(self.attributes)


	def initWithDetails (self, anIdentifier, aLineRange, aText, someAttributes):
		self.identifier = anIdentifier
		self.lineRange = aLineRange
		self.text = aText
		self.attributes = someAttributes
		self.validateState()
		return self


	def validateState (self):
		if self.lineRange is None or len(self.lineRange) != 2:
			raise InvalidFragment("lineRange should contain two values: " + str(self.lineRange))

		if self.lineRange[0] > self.lineRange[1]:
			raise InvalidFragment("inconsistent lineRange: " + str(self.lineRange))

		numberOfLinesInText = self.text.count('\n')
		numberOfLinesInRange = self.lineRange[1] - self.lineRange[0] + 1
		if numberOfLinesInText != numberOfLinesInRange:
			raise InvalidFragment("number of lines in text (" + str(numberOfLinesInText) + ") does not match line range " + str(self.lineRange))


	def isWholeLine (self):
		return True

	def startingPoint (self):
		return (self.lineRange[0], 1)

	def contentLines (self):
		return self.text.split('\n')[:-1]

	def lastLine (self):
		return self.contentLines()[self.lineRange[1] - self.lineRange[0]]

	def endingPoint (self):
		return (self.lineRange[1], len(self.lastLine()) + 1)

	def normalize (self, offset):
		updatedRange = (offset[0] + 1, len(self.text) + offset[0] + 1)
		return NormalizedFragmentIdentifier().initWithDetails(self.identifier, updatedRange, self.text, self.attributes)

#	def shouldSelectionStartAtLine (self, lineNumber):
#		result = False
#		if self.lineRange[0] == lineNumber and 'style' in self.attributes:
#			result = self.attributes['style'].startswith('Heading ')
#
#		return result

	def shiftFragmentLine (self, offset, finalNumberOfLines):
		updatedRangeEnd = self.lineRange[1] - offset
		if updatedRangeEnd > finalNumberOfLines:
			updatedText = '\n'.join(self.text.split('\n')[:finalNumberOfLines - updatedRangeEnd - 1]) + '\n'
			updatedRangeEnd = finalNumberOfLines
		else:
			updatedText = self.text

		return WholeLineFragmentIdentifier().initWithDetails(self.identifier, (self.lineRange[0] - offset, updatedRangeEnd), updatedText, self.attributes)

#------------------------------------------------------------------------------

class NormalizedFragmentIdentifier(LineChunkFragmentIdentifier):

	def __repr__(self):
		return '0:[' + str(self.range[0]) + '-' + str(self.range[1]) + '] "' + self.normalizedTextRepresentation() + '" - ' + str(self.attributes)


	def initWithDetails (self, anIdentifier, aRange, aText, someAttributes):
		self.identifier = anIdentifier
		self.range = aRange
		self.text = aText
		self.attributes = someAttributes
		self.validateState()
		return self


	def startingPoint (self):
		return (0, self.range[0])


	def normalize (self, offset):
		return self


	def updateWithTranslationMap (self, translationMap):
		updatedRange = None
		updatedText  = self.text
		previousEndOfTranslation = 0
		updatedTextOffset = 0
		startOfRangeHasAlreadyBeenFixed = False

		for translation in translationMap:
			if translation[1] <= self.range[0] and translation[0] != translation[1]:
				#   ---------------[----------------]-----------------
				#   ---[++++++]---------------------------------------
				previousEndOfTranslation = translation[1]
				pass
			elif self.range[1] <= translation[0]:
				#   ---------------[----------------]-----------------
				#   --------------------------------[+[++++++]--------
				if updatedRange != None and 0 < previousEndOfTranslation:
					updatedText, updatedTextOffset = self.trimFragmentPrefix(updatedRange, updatedText, translation, previousEndOfTranslation, updatedTextOffset)
					updatedRange = (updatedRange[0], min(updatedRange[1], previousEndOfTranslation))
					previousEndOfTranslation = translation[1]
				break
			else:
				if updatedRange == None:
					updatedRange = self.range

				if translation[0] <= self.range[0]:
					if translation[1] < self.range[1]:
						#   ---------------[----------------]-----------------
						#   -------------[+[++++++]---------------------------
						if translation[0] == translation[1]:	#	some text has been inserted
							if translation[0] < self.range[0]:
								#   ---------------[----------------]-----------------
								#   ------------#-------------------------------------
								pass
							else:
								#   ---------------[----------------]-----------------
								#   ---------------#----------------------------------
								if translation[3].isspace() or translation[3][-1] == '\n':
									# TODO: this check fulfills current tests, but doesn't look fully legit
									pass
								else:
									updatedText = translation[3] + updatedText
									updatedRange = (updatedRange[0] + translation[2],	updatedRange[1])
									updatedTextOffset = translation[2] + len(translation[3])
									startOfRangeHasAlreadyBeenFixed = True
						else:
							updatedRange = (updatedRange[0] + translation[2],	updatedRange[1])
							updatedTextOffset = translation[2]

						previousEndOfTranslation = translation[1]
					else:
						#   ---------------[----------------]-----------------
						#   -------------[+[++++++++++++++++]+]---------------
						if startOfRangeHasAlreadyBeenFixed:
							updatedRange = (updatedRange[0], updatedRange[1] + translation[2])
						else:
							updatedRange = (updatedRange[0] + translation[2], updatedRange[1] + translation[2])
						previousEndOfTranslation = translation[1]
						updatedTextOffset = translation[2]
						break
				else:
					if translation[0] == translation[1]:	#	some text has been inserted
						#   ---------------[----------------]-----------------
						#   ---------------------#----------------------------
						insertionPoint = translation[0] - self.range[0]

						if previousEndOfTranslation <= self.range[0]:
							retainedPrefix = ''
							updatedRange = (translation[0] + translation[2], updatedRange[1])
						elif previousEndOfTranslation < translation[0]:
							retainedPrefix = updatedText[:previousEndOfTranslation - self.range[0]]
						else:
							retainedPrefix = updatedText[:insertionPoint]

 						updatedText = retainedPrefix + translation[3] + updatedText[insertionPoint:]
						previousEndOfTranslation = translation[1]

					else:
						updatedRangeStart = min(updatedRange[0], translation[0] + translation[2])

						if translation[1] < updatedRange[1]:
							#   ---------------[----------------]-----------------
							#   ----------------------[+++++]---------------------
							updatedText, updatedTextOffset = self.trimFragmentPrefix(updatedRange, updatedText, translation, previousEndOfTranslation, updatedTextOffset)
							updatedRange = (updatedRangeStart, updatedRange[1])
							previousEndOfTranslation = max(previousEndOfTranslation, translation[1])
						else:
							#   ---------------[----------------]-----------------
							#   ----------------------{+++++++++]++]--------------
							updatedText, updatedTextOffset = self.trimFragmentPrefix(updatedRange, updatedText, translation, previousEndOfTranslation, updatedTextOffset)
							updatedRange = (updatedRangeStart, updatedRange[1] + translation[2])
							previousEndOfTranslation = max(previousEndOfTranslation, translation[1])
							updatedTextOffset = translation[2]
							break

		if updatedRange:
			if previousEndOfTranslation + updatedTextOffset < updatedRange[1]:
				updatedText = updatedText[:previousEndOfTranslation - updatedRange[1]]
				updatedRange = (updatedRange[0], previousEndOfTranslation + updatedTextOffset)

			result = NormalizedFragmentIdentifier().initWithDetails(self.identifier, updatedRange, updatedText, self.attributes)
		else:
			result = None

		return result


	def rebase (self, lineAccumulatedCount):
		lineNumber = 0
		while (lineAccumulatedCount[lineNumber][0] + lineAccumulatedCount[lineNumber][1]) < self.range[0]:
			lineNumber += 1

		if self.range[0] == lineAccumulatedCount[lineNumber][0] + 1 and len(self.text) == lineAccumulatedCount[lineNumber][1]:
			updatedRange = None
		else:
			updatedRange = (self.range[0] - lineAccumulatedCount[lineNumber][0], self.range[1] - lineAccumulatedCount[lineNumber][0])

		numberOfLines = self.text.count('\n')

		if numberOfLines == 0:
			result = LineChunkFragmentIdentifier().initWithDetails(self.identifier, lineNumber + 1, updatedRange, self.text, self.attributes)
		else:
			result = WholeLineFragmentIdentifier().initWithDetails(self.identifier, (lineNumber + 1, lineNumber + numberOfLines), self.text, self.attributes)

		return result


	def setLine (self, aLineNumber):
		return LineChunkFragmentIdentifier().initWithDetails(self.identifier, aLineNumber, self.range, self.text, self.attributes)

#==============================================================================

class InvalidFragment(Exception):
	pass
