#!/usr/bin/env python3
import random
from os.path import exists
import glob
import sys
import json
from pymongo import MongoClient


def connect_to_mongo(mongo_url, version):

    # Setup Mongo
    try:
        mongo_client = MongoClient(host=mongo_url, serverSelectionTimeoutMS=1000)
        mydb = mongo_client["scheduling_with_simulation"]
        collection = mydb["results_" + version]
    except BaseException as err:
        sys.stderr.write("Cannot connect to MONGO: " + str(err) + "\n")
        sys.exit(1)

    return [collection]


def write_results_to_file(filename, data):
    f = open(filename, "w")
    f.write(str(data) + "\n")
    f.close()
    print("Extracted result dictionary written to file " + filename)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        sys.stderr.write("Usage: " + sys.argv[0] + " <version> <mongo url> [--full]\n")
        sys.stderr.write("  For instance: " + sys.argv[0] + " v3 mongodb://128.171.140.102:443\n")
        sys.exit(1)

    try:
        collections = connect_to_mongo(sys.argv[2], sys.argv[1])
        for collection in collections:
            print(collection.name + ": " + str(collection.count_documents({})))

            if "--full" in sys.argv:
                platform_configurations = set()
                workflow_configurations = set()
                seeds = set()
                cursor = collection.find({})
                for doc in cursor:
                    platform_configurations.add(doc["clusters"])
                    workflow_configurations.add(doc["workflow"])
                    seeds.add(doc["simulation_noise_seed"])
                platform_configurations = sorted(platform_configurations)
                workflow_configurations = sorted(workflow_configurations)
                seeds = sorted(seeds)

                print("PLATFORM:")
                for platform in platform_configurations:
                    count = collection.count_documents({"clusters":platform})
                    print("  " + platform + ": " + str(count))


                print("WORKFLOWS:")
                for workflow in workflow_configurations:
                    count = collection.count_documents({"workflow":workflow})
                    print("  " + workflow + ": " + str(count))

                print("SEEDS:")
                for seed in seeds:
                    count = collection.count_documents({"simulation_noise_seed":seed})
                    print("  " + str(seed) + ": " + str(count))

    except BaseException as err:
        sys.stderr.write("Couldn't connect: " + str(err) + "\n")
        sys.exit(1)

    










