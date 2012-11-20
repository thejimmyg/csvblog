from whoosh.fields import *
# apt-get install python-whoosh

WEBROOT='page'
INDEXDIR='indexdir'

schema = Schema(
    title=TEXT(stored=True), 
    date=TEXT(stored=True), 
    path=ID(stored=True), 
    tag=KEYWORD(stored=True, lowercase=True, commas=True), 
    content=TEXT
)
