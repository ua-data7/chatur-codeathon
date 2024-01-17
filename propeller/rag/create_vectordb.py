import chain
import sys
import os
import pathlib
import shutil
import argparse

from vectordb import VectorDB
from langchain_community.vectorstores import Chroma
from webdav3.client import Client


scratch_root = "./scratch"
vectordb_root = "./vectordb"
webdav_options = {
    'webdav_hostname': "https://data.cyverse.org",
    'webdav_login':    "iychoi",
    'webdav_password': ""
}

webdav_course_material_root = "/dav/iplant/projects/chatur/courses"


def download_course_resource_webdav(course_name:str, no_download:bool) -> str:
    webdav_client = Client(webdav_options)
    
    if not os.path.exists(scratch_root):
        os.mkdir(scratch_root)

    url_path = os.path.join(webdav_course_material_root, course_name)
    target_path = os.path.join(scratch_root, course_name)
    target_path = os.path.abspath(target_path)

    if not no_download:
        print("download %s to %s" % (url_path, target_path))
        webdav_client.download_sync(remote_path=url_path, local_path=target_path)
    return target_path


############################
# Create vector db
############################

parser = argparse.ArgumentParser(
    prog='create_vectordb',
    description='Create vectordb for course materials')

parser.add_argument('--no_download', action='store_true', help='do not download data')
parser.add_argument('--no_delete', action='store_true', help='do not delete data')
parser.add_argument('course_number', help='course number')
args = parser.parse_args()

course_name = args.course_number.upper().strip()

if not os.path.exists(vectordb_root):
    os.mkdir(vectordb_root)

print("create vectordb")
vectordb_path = os.path.join(vectordb_root, course_name)
vectorstore = VectorDB(vectordb_path)

# create
# save file to local
course_material_path = download_course_resource_webdav(course_name, no_download=args.no_download)
course_material = pathlib.Path(course_material_path)

print("adding class materials for %s" % course_name)
for root, dirs, files in os.walk(course_material_path, topdown=True):
    for file in files:
        # file
        fullpath = os.path.join(root, str(file))
        print("> adding '%s'" % fullpath)
        vectorstore.add_file(fullpath)


if not args.no_delete:
    # delete
    print("deleting processed class materials")
    shutil.rmtree(course_material_path)

print("VectorDB for %s is created" % course_name)
