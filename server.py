import os
from wsgiref.simple_server import make_server
# sudo apt-get install python-paste
from paste.urlparser import StaticURLParser
from paste.cascade import Cascade
from search import search
from urlparse import parse_qs
from fastcsv import find_row, headers_from_csv

class QueryError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

def query(root, path, default_format=None, allowed_formats=None, csvfile='data.txt'):
    if allowed_formats is None:
        allowed_formats = ['json', 'html', '']
    # Walk the path tree until an data.txt file is found. Directories after that represent parts of the primary key root
    parts = path.split('/')
    if not parts[0] == '':
        raise QueryError('Path does not start with a /')
    if not len(parts) > 1:
        raise QueryError('Not enough parts in the path')
    directory = root
    filename = None
    for part in parts[1:-1]:
        if not part.strip():
            raise QueryError('Empty path component, ensure the path does not contain // characters together')
    while parts:
        next_part = parts.pop(0)
        directory = os.path.join(directory, next_part)
        if not os.path.exists(directory) or not os.path.isdir(directory):
            if directory == root:
                raise Exception('No such directory %r'%(root,))
            else:
                directory_ = directory[len(root)+1:]
                if directory_:
                    raise QueryError('No such sub directory %r'%(directory_,))
                else:
                    raise QueryError('No such directory %r'%(root,))
        if os.path.exists(os.path.join(directory, csvfile)):
            # Now we have found our CSV file
            filename = os.path.join(directory, csvfile)
            break
        else:
            continue
    if filename is None:
        raise QueryError('No data file found for this path')
    last_part = parts.pop()
    if not last_part.strip():
        raise QueryError('No file part specified')
    if len(last_part.split('.')) == 1:
        if default_format is None:
            raise QueryError('No file extension specified')
    elif not len(last_part.split('.')) == 2:
        raise QueryError('Expected exactly one . character in the last part of the file, to represent the result format')
        #if '.' in part:
        #    raise QueryError('Path parts may not contain a . character')
    if len(last_part.split('.')) == 1:
        id = last_part
        format = default_format
    else:
        id, format = last_part.split('.')
    if format not in allowed_formats:
        raise QueryError('Unknown format. Try a different file extension.')
    key = [x.decode('utf8') for x in parts+[id]]
    header_data, header_length = headers_from_csv(filename)
    rows = find_row(
        filename,
        key, 
    )
    if not rows:
        return None, format
    row_dict = dict(zip(header_data, rows[0]))
    if format == 'json':
        return json.dumps(row_dict), format
    elif format == '':
        return row_dict, format
    elif format == 'html':
        html = row_dict.get('HTMLTemplate', '').strip()
        if not html:
            html = row_dict.get('HTMLTemplate>', '').strip()
            if html:
                with open(os.path.join(os.path.dirname(filename), html), 'rb') as fp:
                    html = fp.read().strip()
        if not html:
            html = """\
<html>
<head><title>%(Title)s</title></head>
<body>
<h1>%(Heading)s</h1>
%(Content)s
</body>
</html>"""
        if not row_dict.get('Title') and not row_dict.get('Heading'):
            row_dict['Title'] = 'Page'
        content = row_dict.get('Content', '').strip()
        if not content:
            content = row_dict.get('Content>', '').strip()
            if content:
                with open(os.path.join(os.path.dirname(filename), content), 'rb') as fp:
                    content = fp.read().strip()
        if not content:
            md = row_dict.get('Content[md]', '').strip()
            if not md:
                md = row_dict.get('Content[md]>', '').strip()
                if md:
                    with open(os.path.join(os.path.dirname(filename), md), 'rb') as fp:
                        md = fp.read().strip()
            if md:
                # sudo apt-get install python-markdown
                import markdown 
                content = markdown.markdown(
                    md.decode('utf8'),
                    [
                        'headerid(level=2)', 
                        'fenced_code', 
                        'nl2br', 
                        #'footnotes',
                        'def_list', 
                        # sudo apt-get install python-pygments
                        # pygmentize -S default -f html > pygments.css
                        # <link rel="stylesheet" type="text/css" href="/pygments.css">
                        'codehilite',
                        #'sane_lists', 
                        'toc',
                    ]
                )
        if not content:
            content = '<p>Data cannot currently be represented as HTML.</p>'
        row_dict['Content'] = content
        if row_dict.get('Title') and not row_dict.get('Heading'):
            row_dict['Heading'] = row_dict['Title']
        elif row_dict.get('Heading') and not row_dict.get('Title'):
            row_dict['Title'] = row_dict['Heading']
        terms = ''
        for term in row_dict['Tags'].split(','):
            if terms:
                terms+= ' OR '
            terms += 'tag:' + term.strip()
        if terms:
            row_dict['TagQuery'] = '('+terms+')'
        else:
            row_dict['TagQuery'] = ''
        result = html%row_dict
        return result, format
    else:
        raise Exception('No such format %r'%(format,))

def query_app(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path == '/search':
        query_string = environ.get('QUERY_STRING', '')
        status = '200 OK'
        content_type = 'text/html'
        body = '<h2>Related Articles</h2><ul>'
        p = parse_qs(query_string.decode('utf8'))
        body += search(p.get('q', [''])[0].decode('utf8'))
        body += '</ul>'
    else:
        accept = environ.get('HTTP_ACCEPT', '')
        default_format = None
        if 'text/html' in accept:
            default_format = 'html'
        elif 'application/json' in accept:
            default_format = 'json'
        path = environ.get('PATH_INFO')
        content_type = 'text/plain'
        try:
            result, format = query(
                '.',
                path,
                default_format, ['json', 'html'],
                csvfile='data.16.csv',
            )
            if result is None:
                body = 'No such record'
                status = '404 No such record'
            else:
                body = result.encode('utf8')
                status = '200 OK'
                if format == 'json':
                    content_type = 'application/json'
                elif format == 'html':
                    content_type = 'text/html'
        except QueryError, e:
            body = unicode(e).encode('utf8')
            status = '500 Query Error'
    start_response(status, [('Content-type', content_type+'; charset=utf8'), ('Content-Length', str(len(body)))])
    return [body]

static_app = StaticURLParser("./")
# Create a cascade that looks for static files first, then tries the web app
app = Cascade([static_app, query_app])

def main():
    httpd = make_server('', 8000, app)
    print "Serving HTTP on port 8000..."
    # Respond to requests until process is killed
    httpd.serve_forever()

if __name__ == '__main__':
    main()


