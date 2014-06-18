# -*- coding: UTF-8 -*-

import os
import shutil

from behave.log_capture import capture

def removeFolder (path):
	try:
		shutil.rmtree(path)
	except:
		pass

def createNewFolder (path):
	removeFolder(path)
	if not os.path.exists(path):
		os.makedirs(path)

# =========================================================

def before_all(context):
	context.sampleFolder			= os.path.join(os.getcwd(), 'samples')
	context.expectedOutcomeFolder	= os.path.join(os.getcwd(), 'samples', 'expected outcome')

def after_all(context):
	removeFolder(os.path.join(os.getcwd(), 'tmp'))
	pass

# ---------------------------------------------------------

def before_scenario(context, scenario):
	context.tmpFolder = os.path.join(os.getcwd(), 'tmp', scenario.name)
	createNewFolder(context.tmpFolder)

#@capture	#	This will capture any logging done during the call to after_scenario and print it out.
def after_scenario(context, scenario):
	removeFolder(context.tmpFolder)
	pass

# =========================================================
