Feature: Text extraction from docx files

Scenario Outline: Basic style and formatting extraction from docx documents
	Given a .docx file <file_to_process>,
	 When it is processed
	 Then the extracted content should match <expected_output>
	  And the extracted formatting should match <expected_output>

	Examples: Simple docs, using just 'Heading 1', and 'Default Style' text with 'bold' and 'italic' chunks.
		| file_to_process                       | expected_output          |
		| docx/01_simple_text.docx              | docx/test_01             |
		| docx/02_paragraph_styles.docx         | docx/test_02             |
		| docx/03_text_formatting.docx          | docx/test_03             |
		| docx/04_mixed_text_formatting.docx    | docx/test_04             |
		| docx/06_new_line_same_paragraph.docx  | docx/test_06             |
		| docx/07_trim.docx                     | docx/test_07             |
		| docx/08_line_blocks.docx              | docx/test_08             |
		| docx/09_toc.docx                      | docx/test_09             |
		| docx/10_line-break.docx               | docx/test_10             |
		| docx/11_weird_formatting.docx         | docx/test_11             |

