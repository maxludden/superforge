# core/clear_md.py

LOG = '/Users/maxludden/dev/py/superforge/log'
fresh_log = "# Superforge Log\n  \n  "

with open (LOG, 'w') as outfile:
    outfile.write(fresh_log)
