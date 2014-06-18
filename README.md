# Description

This library contains a set of tools to work with text documents and their metadata.
It can be used to extract and process metadata, and provides options to generate back full documents that integrate back the original content with the updated metadata.

Its key feature is to completely isolate the handling of document content from the processing of its metadata.


## Extraction
There are a few sample classes of Processor: DocxProcessor, PdfProcessor, and SubstanceProcessor; these classes parse their respective documents and return a Document object that contains both the clear text of the document, and all extracted metadata.

## Processing
Document class provides methods to process metadata; the basic features currently available allow to read/write Document instances to a set of text files (`content.txt`, `formatting.txt`, `metadata.txt`; e.g. `/samples/expected outcome/docx/test_05`), compute the difference between the content of two Document instances (supposedly representing two versions of the same document), and also **update metadata defined for the old version of the documento to match the updated content of the new version**.

This latest feature was the key feature actually driving the development of the library.


## Encoding
At the moment there is only one Generator implemented, and it is the ePubGenerator, that will encode the content and metadata of Document instances in ePub files.



# Current limits
At the moment the Document class supports only two sets of metadata: **formatting** and **metadata**.
The idea was to keep formatting information separated from other types of metadata (annotations, structure, etc…); conceptually thought, being metadata stored outside of the document content, it is possible to conceive the option to extend the library to include an arbitrary set of metadata information, all handled independently one from the other.


# Tests
The library is tested both with unit and feature tests, that can be used also to get an initial understanding on how the library is supposed to be used, while actual documentation is still missing.

## Running tests

	> nosetests && behave

How to run a single UnitTest:

	> nosetests <module.path>:<ClassNameInFile>.<method_name>
	
Examples:

	> nosetests tests/test_fragments_translationMap.py:FragmentIdentifierTranslationMapTests.test_trimmedFragment
	> nosetests tests/test_document_translationMap.py:DocumentTranslationMapTests.test_trim
	
PDF tests temporarly disabled due to a problem installing the library.


# Required libraries

	> pip install nose
	> pip install behave
	> pip install diff_match_patch
	> pip install pdfminer
	> pip install lxml
	
	