Running tests
=============

	> nosetests && behave

	How to run a single UnitTest:
	> nosetests <module.path>:<ClassNameInFile>.<method_name>
	
	Example:
	> nosetests tests/test_fragments_translationMap.py:FragmentIdentifierTranslationMapTests.test_trimmedFragment
	> nosetests tests/test_document_translationMap.py:DocumentTranslationMapTests.test_trim
	
PDF tests temporarly disabled due to a problem installing the library.


Required libraries
------------------

	> pip install nose
	> pip install behave
	> pip install diff_match_patch
	> pip install pdfminer
	> pip install lxml
	
	