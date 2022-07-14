# core/clear_md.py

LOG = '/Users/maxludden/dev/py/superforge/logs/log.md'
new_log = """# *SUPERFORGE* Log
            
<img src="/Users/maxludden/dev/py/superforge/books/book01/Images/gem.gif" alt="gem" width="120" height="60" />

"""

with open (LOG, 'w') as outfile:
    outfile.write(new_log)
