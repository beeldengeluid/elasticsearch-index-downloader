import logging
import sys
from es_index_downloader.index_downloader import IndexDownloader

LOG_FORMAT = "%(asctime)s|%(levelname)s|%(process)d|%(module)s|%(funcName)s|%(lineno)d|%(message)s"

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        stream=sys.stdout,  # configure a stream handler only for now (single handler)
        format=LOG_FORMAT,
    )

    downloader = IndexDownloader()
    downloader.run()
