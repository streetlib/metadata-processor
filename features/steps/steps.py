# -*- coding: UTF-8 -*-

import	os
import	shutil
from	behave	import *

import	main
import	utilities
from	document	import Document

@given('a .docx file {fileToProcess},')
def step(context, fileToProcess):
	context.fileToProcess = os.path.join(context.sampleFolder, fileToProcess)

@given('an initial version of the document ({initialVersion})')
def step(context, initialVersion):
	fileToProcess = os.path.join(context.sampleFolder, initialVersion)
	temporaryFile = os.path.join(context.tmpFolder, 'archivedVersion')
	context.archivedVersion = temporaryFile
	main.processDocx(fileToProcess, temporaryFile)

@given('some metadata {tags}')
def step(context, tags):
	shutil.copy(os.path.join(context.sampleFolder, tags), os.path.join(context.archivedVersion, 'metadata.txt'))

@when('a new version of the document ({newVersion}) is loaded')
def impl(context, newVersion):
	context.fileToProcess = os.path.join(context.sampleFolder, newVersion)

@when('it is processed')
def step(context):
	context.processedFile = os.path.join(context.tmpFolder, 'processedFile')
	main.processDocx(context.fileToProcess, context.processedFile)

@when('it is merged with metadata previously set')
def step(context):
	archivedVersion = Document().initWithFile(context.archivedVersion)
#	archivedVersion.writeTo(os.path.join(context.tmpFolder, '_archived'))
	newVersion = Document().initWithFile(context.processedFile)
#	newVersion.writeTo(os.path.join(context.tmpFolder, '_new'))
	mergedVersion = archivedVersion.mergeWithDocument(newVersion)
	mergedVersionFile = os.path.join(context.tmpFolder, 'mergedVersion')
	mergedVersion.writeTo(mergedVersionFile)
#	mergedVersion.writeTo(os.path.join(context.tmpFolder, '_merged'))
	context.processedFile = mergedVersionFile

@then('the extracted content should match {expectedResult}')
def step(context, expectedResult):
	assert utilities.compareProcessedFileWithExpectedResult(context, expectedResult, 'content.txt')

@then('the extracted formatting should match {expectedResult}')
def step(context, expectedResult):
#	assert utilities.compareProcessedFileWithExpectedResult(context, expectedResult, 'formatting.txt')
	assert utilities.compareFormattings(context, expectedResult)

@then('the extracted metadata should match {expectedResult}')
def step(context, expectedResult):
	assert utilities.compareProcessedFileWithExpectedResult(context, expectedResult, 'metadata.txt')
