# elasticsearch-index-downloader
Command line tool for downloading an Elasticsearch index as JSON files per document type

#How to setup & use

This script is made for Python 3 (3.6 to be exact)

Make sure to install [pip](https://pypi.python.org/pypi/pip/) and [virtualenv](https://pypi.python.org/pypi/virtualenv).

Make sure to check which version of Python 3 you have installed, then run the following command with the exact version:

<code>
	virtualenv -p python3.x venv
</code>

After the virtual environment is created, activate your virtualenv with:

<code>
	. venv/bin/activate
</code>

After that go to the main dir of this repo so you can install the required Python libraries by running:

<code>
	pip install -r requirements.txt
</code>

Now you're ready to run the script with:

<code>
	python ./IndexDownloader.py
</code>

You'll get a series of input questions and if all your settings are correct you might as well be downloading a pipin' hot Elasticsearch index in minutes!