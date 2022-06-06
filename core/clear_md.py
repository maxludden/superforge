# core/clear_md.py
LOG = '''# SuperForge Log

'''
path = '/Users/maxludden/dev/py/superforge/logs/log.md'
with open (path, 'w') as outfile:
    outfile.write(LOG)
    
print("Reset log.md")