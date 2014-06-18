Feature: Merge changes present in an updated version of the uploaded document

# Background: A previous version of the document was already uploaded and tagged
# 	Given an <initial_version> of the document
# 	  And some metadata <tags>

Scenario Outline: When a new document is loaded, changes are integrated
	Given an initial version of the document (<initial_version>)
	  And some metadata <tags>
	 When a new version of the document (<new_version>) is loaded
	  And it is processed
	  And it is merged with metadata previously set
	 Then the extracted content should match <expected_output>
	  And the extracted metadata should match <expected_output>

	Examples: Simple docs, using just 'Heading 1', and 'Default Style' text with 'bold' and 'italic' chunks.
		| initial_version          | tags                  | new_version               | expected_output     |
		| docx/05_version_0.1.docx | tags/05_metadata.txt  | docx/05_version_0.2.docx  | docx/test_05        |


