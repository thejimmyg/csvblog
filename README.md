# CSVBlog

Pure Python blog running off a CSV index with Markdown content.

Very much a work in progress.

## License

[GNU AGPL3](http://www.gnu.org/licenses/agpl-3.0.html).

## Install

~~~
sudo apt-get install python-markdown python-whoosh python-pastescript
~~~

You'll also need the `fastcsv.py` file from the [fastcsv repo](https://github.com/thejimmyg/fastcsv):

~~~
wget https://raw.github.com/thejimmyg/fastcsv/master/fastcsv.py
~~~

## Getting Started

Read the index.html file.

## CSV Tests

Note the tests don't pass at the moment. Don't worry about that

~~~
wget http://data.gov.uk/data/dumps/data.gov.uk-ckan-meta-data-2012-11-14.csv.zip
unzip data.gov.uk-ckan-meta-data-2012-11-14.csv.zip
mv data.gov.uk-ckan-meta-data-2012-11-14.csv bigtest.csv
python csvtools.py
~~~

