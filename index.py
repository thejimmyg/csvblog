"""
Index a website for search

~~~
mkdir indexdir
python index.py 
"""
import os
import whoosh.index
from search_common import * 
from fastcsv import lex, headers_from_csv
from datetime import datetime

csv = os.path.join(WEBROOT, 'data.16.csv')
headers, length = headers_from_csv(csv)
rows = []
def row_callback(row, end_pos):
    row_dict = {}
    for i, header in enumerate(headers):
        row_dict[header] = row[i]
    rows.append(row_dict)
    return True
count, r =  lex(csv, length+1, row_callback, rows=None)
print "Found %s documents"%(len(rows))
if not os.path.exists(INDEXDIR):
    os.mkdir(INDEXDIR)
ix = whoosh.index.create_in(INDEXDIR, schema)
writer = ix.writer()
counter = 0
for row in rows:
    content = row.get("Content", "").strip()
    if not content:
        content = row.get("Content[md]", "").strip()
    if not content:
        filename = row["Content[md]>"]
        with open(os.path.join(WEBROOT, filename), 'rb') as doc:
            content = doc.read()
    if not content:
        print "Skipping document, no content"
    else:
        try:
            date=datetime.strptime(row['Date'].decode('utf8'), '%Y-%m-%d %H:%M')
        except ValueError: 
            try:
                date=datetime.strptime(row['Date'].decode('utf8'), '%Y-%m-%d')
            except ValueError: 
                date=datetime(1970,1,1,0,0,0)
        writer.add_document(
            title=row['Title'].decode('utf8'),
            tag=row['Tags'].decode('utf8'),
            path=u"/"+row['Name'].decode('utf8'),
            date=date,
            content=content.decode('utf8'),
        )
        counter += 1
writer.commit()
print "Indexed %d documents"%(counter,)
