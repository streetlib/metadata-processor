#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import	sys
import	os
from	docx		import	DocxProcessor

def createFolder (path):
	if not os.path.exists(path):
		os.makedirs(path)

# =========================================================

def processDocx (docxFile, targetFolder):
	docxProcessor = DocxProcessor(docxFile)
	document = docxProcessor.document()
	document.writeTo(targetFolder)

# =========================================================

def main ():
	try:
		processDocx(sys.argv[1], sys.argv[2])
	except:
		print('Please supply an input and output file. For example:')    
		print('''  example-extracttext.py 'My Office 2007 document.docx' 'outputfile' ''')    
		exit()

# =========================================================
	
if __name__ == '__main__':        
	main()
