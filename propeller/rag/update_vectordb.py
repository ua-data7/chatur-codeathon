import chain
import sys
import os
from vectordb import VectorDB

from langchain_community.vectorstores import Chroma

vectordb_root = "./vectordb"

############################
# Create or update vector db
############################

# arg 1: identifier (e.g., class name)
# args 2-: files/urls

input_args = sys.argv[1:]
if len(input_args) < 2:
    print("give [identifier] and [files/urls] as arguments")
    exit(1)

identifier = str.strip(str.lower(input_args[0]))
input_paths = input_args[1:]

if not os.path.exists(vectordb_root):
    os.mkdir(vectordb_root)

vectordb_path = vectordb_root + identifier
vectorstore = VectorDB(vectordb_path)

# create or update
for input_path in input_paths:
    print("> input: " + input_path)
    # todo: read from webdav
    vectorstore.add_file(input_path)

print("VectorDB creation/update for %s Done" % identifier)
