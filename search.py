import sys
from whoosh.qparser import QueryParser
import whoosh.index
from search_common import * 
from whoosh.index import open_dir
from whoosh import sorting

ix = open_dir(INDEXDIR)

def search(term):
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(term)
        date_sort_facet = sorting.FieldFacet("date", reverse=True)
        results = searcher.search(query, sortedby=date_sort_facet)
        links = []
        for x in results:
            links.append('<li><a href="'+x['path']+'.html'+'">'+x['title']+'</a></li>\n')
        return u"".join(links).encode('utf8')

if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print "Usage: python search.py \"(tag:two OR content:visitor)\""
        sys.exit(-1)
    print search(sys.argv[1].decode('utf8'))
