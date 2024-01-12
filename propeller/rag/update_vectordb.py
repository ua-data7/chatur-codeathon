import chain
import sys
import os
from vectordb import VectorDB

from langchain_community.vectorstores import Chroma
from webdav3.client import Client
from urllib.parse import urlparse

scratch_root = "./scratch"
vectordb_root = "./vectordb"
webdav_options = {
    'webdav_hostname': "https://data.cyverse.org",
    'webdav_login':    "",
    'webdav_password': ""
}

webdav_vectordb_root = "/dav/iplant/projects/chatur/vectordb"



def download_resource_webdav(coursename:str, url:str) -> str:
    webdav_client = Client(webdav_options)
    
    scratch_path = scratch_root + coursename
    if not os.path.exists(scratch_path):
        os.mkdir(scratch_path)


    parsedurl = urlparse(url)
    filename = os.path.basename(parsedurl.path).split('/')[-1]

    target_path = os.path.join(scratch_path, coursename)
    print("download %s to %s" % (parsedurl.path, target_path))
    webdav_client.download_sync(remote_path=parsedurl.path, local_path=target_path)
    return target_path


def download_vectordb_webdav(coursename:str):
    webdav_client = Client(webdav_options)
    target_path = os.path.join(webdav_vectordb_root, coursename)
    if webdav_client.check(target_path):
        webdav_client.download_sync(remote_path=target_path, local_path=vectordb_root)


def upload_vectordb_webdav(coursename:str):
    vectordb_path = os.path.join(vectordb_root, coursename)
    webdav_client = Client(webdav_options)
    target_path = os.path.join(webdav_vectordb_root, coursename)
    webdav_client.upload_sync(remote_path=target_path, local_path=vectordb_path)



############################
# Create or update vector db
############################

# arg 1: coursename
# args 2-: files/urls

input_args = sys.argv[1:]
if len(input_args) < 2:
    print("give [course_name] and [files/urls] as arguments")
    exit(1)

coursename = input_args[0].upper().strip()
input_paths = input_args[1:]

if not os.path.exists(vectordb_root):
    os.mkdir(vectordb_root)

print("download vectordb for course %s" % coursename)
download_vectordb_webdav(coursename)

print("create/update vectordb")
vectordb_path = os.path.join(vectordb_root, coursename)
vectorstore = VectorDB(vectordb_path)

# create or update
for input_path in input_paths:
    print("> input: " + input_path)
    if input_path.startswith("http://") or input_path.startswith("https://"):
        # save file to local
        local_filepath = download_resource_webdav(coursename, input_path)
        vectorstore.add_file(local_filepath)
        # delete
        os.remove(local_filepath)
    else:
        vectorstore.add_file(input_path)


print("upload vectordb for course %s" % coursename)
upload_vectordb_webdav(coursename)

print("VectorDB creation/update for %s Done" % coursename)
