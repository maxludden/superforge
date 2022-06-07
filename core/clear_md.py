# core/clear_md.py
LOG = '''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
	<meta charset="utf-8"/>
	<title>SuperForge Log</title>
	<link type="text/css" rel="stylesheet" href="../Styles/style.css"/>
	<meta name="viewport" content="width=device-width"/>
</head>
<body>
'''
path = '/Users/maxludden/dev/py/superforge/logs/log.md'
with open (path, 'w') as outfile:
    outfile.write(LOG)
    
print("Reset log.md")