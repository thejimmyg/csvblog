import sys
from whoosh.qparser import QueryParser
import whoosh.index
from search_common import * 
from whoosh.index import open_dir

ix = open_dir(INDEXDIR)

def search(term):
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(term)
        results = searcher.search(query)
        links = []
        for x in results:
            links.append('<li><a href="/page'+x['path']+'.html'+'">'+x['title']+'</a></li>\n')
        return u"".join(links).encode('utf8')

if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print "Usage: python search.py \"(tag:two OR content:visitor)\""
        sys.exit(-1)
    print search(sys.argv[1].decode('utf8'))
