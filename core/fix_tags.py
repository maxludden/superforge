# core/fix_tags.py
LOG = "/Users/maxludden/dev/py/superforge/logs/log.md"
def fix_tags():
    with open (LOG, 'r') as infile:
        md = infile.read()
        
    md = md.replace('\<','<')
    fixed_md = md.replace('\n            </pre>', '            </pre>')
    with open (LOG, 'w') as outfile:
        outfile.write(fixed_md)

fix_tags()