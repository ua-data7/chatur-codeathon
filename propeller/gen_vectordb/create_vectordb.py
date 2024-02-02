import os
import pathlib
import argparse
import shutil
import tarfile
import zipfile

from vectordb import VectorDB
from webdav3.client import Client


scratch_root = "./scratch"
scratch_inter_root = "./scratch_intermediate"
vectordb_root = "./vectordb"
webdav_options = {
    'webdav_hostname': "https://data.cyverse.org",
    'webdav_login':    "anonymous",
    'webdav_password': "anonymous_password"
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
parser.add_argument('--create_docs', action='store_true', help='create intermediate docs')
parser.add_argument('--add_db', action='store_true', help='do not clear db and intermediate docs, it will add to existing db')
parser.add_argument('course_number', help='course number')
args = parser.parse_args()

course_name = args.course_number.upper().strip()

os.makedirs(vectordb_root, exist_ok=True)

if args.create_docs:
    os.makedirs(scratch_inter_root, exist_ok=True)

# create
# save file to local
course_material_path = download_course_resource_webdav(course_name, no_download=args.no_download)
course_material = pathlib.Path(course_material_path)

intermedate_doc_output_path = os.path.join(scratch_inter_root, course_name)
intermedate_doc_output_path = os.path.abspath(intermedate_doc_output_path)

vectordb_path = os.path.join(vectordb_root, course_name)
vectordb_path = os.path.abspath(vectordb_path)

if not args.add_db:
    # clear db
    if os.path.exists(vectordb_path):
        print("removing old vectordb - %s" % vectordb_path)
        shutil.rmtree(vectordb_path)

    if os.path.exists(intermedate_doc_output_path):
        print("removing old doc - %s" % intermedate_doc_output_path)
        shutil.rmtree(intermedate_doc_output_path)

print("creating vectordb - %s" % vectordb_path)
vectorstore = VectorDB(vectordb_path)

print("check tarballs/zip files")
for root, dirs, files in os.walk(course_material_path, topdown=True):
    for file in files:
        # file
        fullpath = os.path.join(root, str(file))
        dirpath = os.path.dirname(fullpath)

        if file.startswith("~"):
            # ignore temp files
            continue

        if file.lower().endswith(".tar") or file.lower().endswith(".tar.gz"):
            print("extracting %s" % fullpath)
            if tarfile.is_tarfile(fullpath):
                # extract
                tarfilepath = os.path.join(dirpath, file + ".extracted")
                os.makedirs(tarfilepath, exist_ok=True)
                tfile = tarfile.open(fullpath)
                tfile.extractall(tarfilepath)
                tfile.close()
        elif file.lower().endswith(".zip"):
            print("extracting %s" % fullpath)
            if zipfile.is_zipfile(fullpath):
                # extract
                zipfilepath = os.path.join(dirpath, file + ".extracted")
                os.makedirs(zipfilepath, exist_ok=True)

                with zipfile.ZipFile(fullpath) as zfile:
                    zfile.extractall(zipfilepath)


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

        if file.lower().endswith(".tar") or file.lower().endswith(".tar.gz") or file.lower().endswith(".zip"):
            # ignore, already extracted
            continue

        print("> adding '%s'" % fullpath)

        if args.create_docs:
            print("> intermediate output '%s'" % docpath)
            vectorstore.add_file(path=fullpath, source=relpath, doc_output_path=docpath)
        else:
            vectorstore.add_file(path=fullpath, source=relpath)


print("VectorDB for %s is created" % course_name)
