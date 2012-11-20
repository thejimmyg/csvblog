from whoosh.qparser import QueryParser
import whoosh.index

from search_common import * 
from whoosh.index import open_dir

ix = open_dir(INDEXDIR)

#r = None
#with ix.searcher() as searcher:
#    query = QueryParser("content", ix.schema).parse(u"javascript")
#    results = searcher.search(query)
#    for x in results:
#        print x['title']

def search(term):
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(term)
        results = searcher.search(query)
        links = []
        for x in results:
            links.append('<li><a href="/page'+x['path'][:-3]+'.html'+'">'+x['title']+'</a></li>')
        return u"".join(links).encode('utf8')


