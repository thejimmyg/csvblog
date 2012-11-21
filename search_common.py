from whoosh.fields import *
# apt-get install python-whoosh

WEBROOT='page'
PORT = 8080
INDEXDIR='indexdir'

schema = Schema(
    title=TEXT(stored=True), 
    date=DATETIME(stored=True), 
    path=ID(stored=True), 
    tag=KEYWORD(stored=True, lowercase=True, commas=True), 
    content=TEXT
)
