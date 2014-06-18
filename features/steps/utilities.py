# -*- coding: UTF-8 -*-

import	os
import	filecmp

from	document	import	Document


def compareProcessedFileWithExpectedResult(context, expectedResult, fileName):
	processedFile	= os.path.join(context.processedFile, fileName)
	expectedOutput	= os.path.join(context.expectedOutcomeFolder, expectedResult, fileName)

#	print('isfile(processedFile):  ' + str(os.path.isfile(processedFile)))
#	print('isfile(expectedOutput): ' + str(os.path.isfile(expectedOutput)))
	if os.path.isfile(processedFile) and os.path.isfile(expectedOutput):
#	if processedFile and expectedOutput:
		result = filecmp.cmp(processedFile, expectedOutput, shallow=False)
	elif not os.path.isfile(processedFile) and not os.path.isfile(expectedOutput):
		result = True
	else:
		result = False

	return result

def compareFormattings(context, expectedResult):
	document = Document().initWithFile(context.processedFile)
	expectedDocument = Document().initWithFile(os.path.join(context.expectedOutcomeFolder, expectedResult))

	return cmp(document.formatting(), expectedDocument.formatting()) == 0