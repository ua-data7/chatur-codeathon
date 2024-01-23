import os
import pathlib
import shutil
import argparse

from vectordb import VectorDB
from webdav3.client import Client


scratch_root = "./scratch"
scratch_inter_root = "./scratch_intermediate"
vectordb_root = "./vectordb"
webdav_options = {
    'webdav_hostname': "https://data.cyverse.org",
    'webdav_login':    "anonymous",
    'webdav_password': ""
}

webdav_course_material_root = "/dav/iplant/projects/chatur/courses"


def download_course_resource_webdav(course_name:str, no_download:bool) -> str:
    webdav_client = Client(webdav_options)
    
    os.makedirs(scratch_root, exist_ok=True)

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
parser.add_argument('--create_docs', action='store_true', help='create intermediate docs')
parser.add_argument('course_number', help='course number')
args = parser.parse_args()

course_name = args.course_number.upper().strip()

os.makedirs(vectordb_root, exist_ok=True)

if args.create_docs:
    os.makedirs(scratch_inter_root, exist_ok=True)
        

print("create vectordb")
vectordb_path = os.path.join(vectordb_root, course_name)
vectorstore = VectorDB(vectordb_path)

# create
# save file to local
course_material_path = download_course_resource_webdav(course_name, no_download=args.no_download)
course_material = pathlib.Path(course_material_path)

intermedate_doc_output_path = os.path.join(scratch_inter_root, course_name)
intermedate_doc_output_path = os.path.abspath(intermedate_doc_output_path)

print("adding class materials for %s" % course_name)
for root, dirs, files in os.walk(course_material_path, topdown=True):
    for file in files:
        # file
        fullpath = os.path.join(root, str(file))
        relpath = os.path.relpath(fullpath, course_material_path)

        docpath = os.path.join(intermedate_doc_output_path, relpath)
        docpath = docpath + ".dump"

        if file.startswith("~"):
            # ignore temp files
            print("> ignore temp file '%s'" % fullpath)
            continue
        
        print("> adding '%s'" % fullpath)

        if args.create_docs:
            print("> intermediate output '%s'" % docpath)
            vectorstore.add_file(fullpath, docpath)
        else:
            vectorstore.add_file(fullpath)


if not args.no_delete:
    # delete
    print("deleting processed class materials")
    shutil.rmtree(course_material_path)

print("VectorDB for %s is created" % course_name)
