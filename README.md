# elasticsearch-index-downloader
Command line tool for downloading an Elasticsearch index as JSON files per document type

# How to setup & use

This script is made for Python 3, but with minor changes it can also run on Python 2.x (see the inline comments in the code)

Make sure to install [pip](https://pypi.python.org/pypi/pip/) and [virtualenv](https://pypi.python.org/pypi/virtualenv).

Make sure to check which version of Python 3 you have installed, then run the following command with the exact version:

```
virtualenv -p python3.x venv
```

After the virtual environment is created, activate your virtualenv with:

```
. venv/bin/activate
```

After that go to the main dir of this repo so you can install the required Python libraries by running:

```
pip install -r requirements.txt
```

And finally you're ready to run the script with:

```
python ./IndexDownloader.py
```

which'll give you a series of input questions. After answering them all flawlessly you'll be downloading a pipin' hot Elasticsearch index in no time!
