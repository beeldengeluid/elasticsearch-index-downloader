import json
import os
import logging
from elasticsearch7 import Elasticsearch
from elasticsearch7.client import IndicesClient


logger = logging.getLogger(__name__)
DEFAULT_ES_HOST = "localhost"
DEFAULT_ES_PORT = 9200
DEFAULT_INDEX_NAME = "slartibartfast"
DEFAULT_OUTPUT_DIR = "output"

"""
This class enables exporting an Elasticsearch index into an output directory of choice
creating JSON files (of a desirable size) per doc_type
"""


class IndexDownloader:
    def __init__(self):
        pass

    # NOTE if you run this with Python 2.x all input() functions must be changed to raw_input()
    def run(self):
        print(
            f"Please enter the elasticsearch host (default: {DEFAULT_ES_HOST}):"
        )
        esHost = input() or DEFAULT_ES_HOST
        print("\n\tUsing host: %s" % esHost)

        print(
            f"\nPlease enter the elasticsearch port (default: {DEFAULT_ES_PORT}):"
        )
        esPort = input() or DEFAULT_ES_PORT
        print("\n\tUsing port: %s" % esPort)

        # testing if the host & port connect
        es = None
        esInfo = None
        try:
            es = Elasticsearch(host=esHost, port=esPort)
            esInfo = es.info()
            print("\n\tConnection to Elasticsearch successful")
        except Exception as err:
            print(err)
            print(
                "\n\tAborting: could not connect to Elasticsearch hosted on %s:%s"
                % (esHost, esPort)
            )
            quit()

        print(
            f"\nPlease enter an index name to be downloaded (default: {DEFAULT_INDEX_NAME})"
        )
        indexName = input() or DEFAULT_INDEX_NAME
        iclient = IndicesClient(es)

        # If specified, delete any existing index with the same name
        if not iclient.exists(indexName):
            print("\n\tAborting: index %s does not exist" % indexName)
            quit()

        print("\n\tIndex %s exists and is now selected for download" % indexName)

        print(
            f"\nPlease enter the directory path where the index data should be downloaded (default: {DEFAULT_OUTPUT_DIR})"
        )
        outputDir = input() or DEFAULT_OUTPUT_DIR
        outputDir = os.path.abspath(outputDir)

        print("\n\tChecking if dir %s exists" % outputDir)

        # check if the output dir exists, offer the user an option of creating it
        if not os.path.exists(outputDir):
            print("\nDirectory %s does not exist, create it? (y/n)" % outputDir)
            x = input()
            if x == "y":
                try:
                    os.mkdir(outputDir)
                except Exception:
                    print(
                        "\n\tAborting: only a single subdirectory will be created for you, \
                        please specify a parent directory or create the directory yourself"
                    )
                    quit()
            else:
                print("\n\tAborting: no output directory available")
                quit()

        # check if the entered path is a directory
        if not os.path.isdir(outputDir):
            print(
                "\n\tAborting: the path you entered does not point to a directory"
            )
            quit()

        # if the output dir is valid
        print("\n\tDir exists, continuing")
        print(
            "\nPlease enter the maximum file size in megabytes of the dump files (default: 20)"
        )
        maxFileSize = input() or 20
        try:
            maxFileSize = int(maxFileSize)
        except ValueError:
            print(
                "\n\tYou did not enter a valid integer, so continuing with the default of 20 Mb"
            )
            maxFileSize = 20

        print("\n\tWe're all set, so let's go!")
        self.export(es, esInfo, indexName, outputDir, maxFileSize * 1024 * 1024)

    def export(self, es, esInfo, indexName, outputDir, maxFileSize=100 * 1024 * 1024):
        logger.info("exporting index to : %s" % outputDir)
        # continue with the real work
        fileHandles = {}
        query = {"query": {"match_all": {}}, "size": 50}
        resp = es.search(index=indexName, body=query, scroll="10m", request_timeout=36000)
        if resp and "_scroll_id" in resp and len(resp["hits"]["hits"]) > 0:
            self.writeToFile(
                outputDir, indexName, fileHandles, resp["hits"]["hits"], maxFileSize
            )
            scrollId = resp["_scroll_id"]
            count = 1
            while True:
                logger.info("%d => %s" % (count, scrollId))
                if int(esInfo["version"]["number"][0:1]) < 5:
                    scroll = es.scroll(scroll_id=scrollId, body=scrollId, scroll="10m")
                else:
                    scroll = es.scroll(scroll_id=scrollId, scroll="10m")
                if (
                    scroll
                    and "_scroll_id" in scroll
                    and len(scroll["hits"]["hits"]) > 0
                ):
                    scrollId = scroll["_scroll_id"]
                    logger.info(scroll["hits"]["hits"][0]["_id"])
                    self.writeToFile(
                        outputDir,
                        indexName,
                        fileHandles,
                        scroll["hits"]["hits"],
                        maxFileSize,
                    )
                else:
                    logger.info("\t\t All done!")
                    break
                count += 1

            logger.info("clearing the scroll window")
            if int(esInfo["version"]["number"][0:1]) < 5:
                es.clear_scroll(scroll_id=scrollId, body=scrollId)
            else:
                es.clear_scroll(scroll_id=scrollId)

            logger.info("closing all file handles")
            for k in fileHandles.keys():
                fileHandles[k][len(fileHandles[k]) - 1].write("]")
                fileHandles[k][len(fileHandles[k]) - 1].close()

    # writes the hits to a file related to the document type. Files will be kept smaller than maxFileSize
    def writeToFile(self, outputDir, indexName, fileHandles, hits, maxFileSize):
        for hit in hits:
            dumpFile = None
            if hit["_type"] in fileHandles:
                dumpFile = "_%s__%s_%03d.json" % (
                    indexName,
                    hit["_type"],
                    len(fileHandles[hit["_type"]]) - 1,
                )

                if (
                    os.stat(os.path.join(outputDir, dumpFile)).st_size < maxFileSize
                ):  # don't make em bigger than 100 Mb
                    # add the hit to the current JSON file
                    fileHandles[hit["_type"]][len(fileHandles[hit["_type"]]) - 1].write(
                        ","
                    )
                    fileHandles[hit["_type"]][len(fileHandles[hit["_type"]]) - 1].write(
                        json.dumps(hit)
                    )
                else:
                    # properly finish the previous JSON file and close the file handler
                    fileHandles[hit["_type"]][len(fileHandles[hit["_type"]]) - 1].write(
                        "]"
                    )
                    fileHandles[hit["_type"]][
                        len(fileHandles[hit["_type"]]) - 1
                    ].close()

                    # create a new file with an increased trailing number and add the hit there
                    dumpFile = "_%s__%s_%03d.json" % (
                        indexName,
                        hit["_type"],
                        len(fileHandles[hit["_type"]]),
                    )
                    f = open(os.path.join(outputDir, dumpFile), "w")
                    fileHandles[hit["_type"]].append(f)

                    fileHandles[hit["_type"]][len(fileHandles[hit["_type"]]) - 1].write(
                        "["
                    )
                    fileHandles[hit["_type"]][len(fileHandles[hit["_type"]]) - 1].write(
                        json.dumps(hit)
                    )
            else:  # first file of the doc type, so create a new file with trailing number 0
                dumpFile = "_%s__%s_%03d.json" % (indexName, hit["_type"], 0)
                f = open(os.path.join(outputDir, dumpFile), "w")
                fileHandles[hit["_type"]] = [f]
                fileHandles[hit["_type"]][len(fileHandles[hit["_type"]]) - 1].write("[")
                fileHandles[hit["_type"]][len(fileHandles[hit["_type"]]) - 1].write(
                    json.dumps(hit)
                )
