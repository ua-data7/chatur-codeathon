#!/usr/bin/env python3

import os
import pathlib
import argparse
import shutil
import tarfile
import zipfile
import requests
import base64

from urllib.parse import urlparse
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

def get_extension_for_content_type(content_type:str) -> str:
    content_type_arr = content_type.split(";")
    for content_type in content_type_arr:
        match content_type:
            case "text/html" | "application/xhtml+xml":
                return "html"
            case "application/pdf":
                return "pdf"
            case "application/vnd.ms-powerpoint":
                return "ppt"
            case "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                return "pptx"
            case "text/plain":
                return "txt"
            case "application/msword" | "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return "docx"
            case "text/markdown":
                return "md"
            case _:
                pass
    
    return "unknown"

def download_web_resource(url:str, output_path:str) -> None:
    print("retrieving data from url %s" % url)
    r = requests.get(url)

    content_type = r.headers["Content-Type"]
    urlobj = urlparse(url)
    fileext = ""
    
    if len(urlobj.path) > 0:
        fileext = pathlib.Path(urlobj.path).suffix
        if not fileext:
            newext = get_extension_for_content_type(content_type)
            if newext:
                fileext = "." + newext
    
    output_path_url = os.path.join(output_path, "b64:" + base64.b64encode(url.encode("ascii")).decode("ascii"))
    output_path_url = output_path_url + fileext

    with open(output_path_url, "w") as f:
        f.write(r.text)
    
def is_file_ignored(name:str) -> bool:
    if name.startswith("~"):
        # ignore temp files
        return True
    return False

def is_bundle_file(name:str) -> bool:
    lname = name.lower()
    if lname.endswith(".tar") or lname.endswith(".tar.gz") or lname.endswith(".zip") or lname.endswith(".url"):
        return True
    return False

def extract_bundle_files(course_material_path:str) -> None:
    for root, _, files in os.walk(course_material_path, topdown=True):
        for file in files:
            # file
            fullpath = os.path.join(root, file)
            dirpath = root

            if is_file_ignored(file):
                continue

            if file.lower().endswith(".tar") or file.lower().endswith(".tar.gz"):
                print("extracting %s" % fullpath)
                if tarfile.is_tarfile(fullpath):
                    # extract
                    tarfilepath = os.path.join(dirpath, file + ".extracted")
                    if os.path.exists(tarfilepath):
                        print("skip. path already exists %s" % tarfilepath)
                        continue

                    os.makedirs(tarfilepath, exist_ok=True)
                    tfile = tarfile.open(fullpath)
                    tfile.extractall(tarfilepath)
                    tfile.close()
            elif file.lower().endswith(".zip"):
                print("extracting %s" % fullpath)
                if zipfile.is_zipfile(fullpath):
                    # extract
                    zipfilepath = os.path.join(dirpath, file + ".extracted")
                    if os.path.exists(zipfilepath):
                        print("skip. path already exists %s" % zipfilepath)
                        continue
                    
                    os.makedirs(zipfilepath, exist_ok=True)

                    with zipfile.ZipFile(fullpath) as zfile:
                        zfile.extractall(zipfilepath)
            elif file.lower().endswith(".url"):
                print("downloading %s" % fullpath)
                webpath = os.path.join(dirpath, file + ".downloaded")
                if os.path.exists(webpath):
                    print("skip. path already exists %s" % webpath)
                    continue
                
                os.makedirs(webpath, exist_ok=True)

                with open(fullpath, "r") as url_f:
                    for line in url_f.readlines():
                        if line.strip().startswith("#"):
                            continue

                        if len(line.strip()) == 0:
                            continue

                        download_web_resource(line.strip(), webpath)

############################
# Create vector db
############################
def main() -> None:
    parser = argparse.ArgumentParser(
        prog='create_vectordb',
        description='Create vectordb for course materials')

    parser.add_argument('--no_download', action='store_true', help='do not download data')
    parser.add_argument('--create_docs', action='store_true', help='create intermediate docs')
    parser.add_argument('--delete_old', action='store_true', help='delete old db and intermediate docs')
    parser.add_argument('--create_allinone', action='store_true', help='create all-in-one db')
    parser.add_argument('--prepare_source', action='store_true', help='prepare source only (download and extract)')
    parser.add_argument('course_numbers', nargs="+", help='course number')
    args = parser.parse_args()

    for course_number in args.course_numbers:
        course_name = course_number.upper().strip()

        os.makedirs(vectordb_root, exist_ok=True)

        if args.create_docs:
            os.makedirs(scratch_inter_root, exist_ok=True)

        # create
        # save file to local
        course_material_path = download_course_resource_webdav(course_name, no_download=args.no_download)
        
        intermedate_doc_output_path = os.path.join(scratch_inter_root, course_name)
        intermedate_doc_output_path = os.path.abspath(intermedate_doc_output_path)

        vectordb_path = os.path.abspath(vectordb_root)

        if args.delete_old:
            # clear
            if os.path.exists(vectordb_path):
                print("removing old vectordb - %s" % vectordb_path)
                shutil.rmtree(vectordb_path)

            if os.path.exists(intermedate_doc_output_path):
                print("removing old doc - %s" % intermedate_doc_output_path)
                shutil.rmtree(intermedate_doc_output_path)

        collection_name = "langchain"
        if not args.create_allinone:
            vectordb_path = os.path.join(vectordb_path, course_name)
        else:
            collection_name = course_name

        print("creating vectordb - %s, collection - %s" % (vectordb_path, collection_name))
        vectorstore = VectorDB(db_path=vectordb_path, collection_name=collection_name)

        print("check tarballs/zip files")
        extract_bundle_files(course_material_path)

        if args.prepare_source:
            continue
            
        print("adding class materials for %s" % course_name)
        for root, dirs, files in os.walk(course_material_path, topdown=True):
            for file in files:
                # file
                fullpath = os.path.join(root, file)
                relpath = os.path.relpath(fullpath, course_material_path)

                docpath = os.path.join(intermedate_doc_output_path, relpath)
                docpath = docpath + ".dump"

                source = relpath
                if file.startswith("b64:"):
                    newfile = file[4:].split(".")[0]
                    source = base64.b64decode(newfile).decode("ascii")

                if is_file_ignored(file):
                    # ignore temp files
                    print("> ignore temp file '%s'" % fullpath)
                    continue
                
                if is_bundle_file(file):
                    # ignore, already extracted
                    continue

                print("> adding '%s'" % fullpath)

                if args.create_docs:
                    print("> intermediate output '%s'" % docpath)
                    vectorstore.add_file(path=fullpath, source=source, doc_output_path=docpath)
                else:
                    vectorstore.add_file(path=fullpath, source=source)


        print("VectorDB for %s is created" % course_name)


if __name__ == "__main__":
    main()
