#!/usr/bin/env python3

import os
import chain
import argparse
from vectordb_reader import VectorDBReader
from langchain.globals import set_debug

set_debug(True)

vectordb_root = "./vectordb"


parser = argparse.ArgumentParser(
    prog='test_chat',
    description='Chat about course materials')

parser.add_argument('--no_vectordb', action='store_true', help='do not use vector db')
parser.add_argument('course_number', nargs='?', help='course number')
args = parser.parse_args()

if not args.no_vectordb:
    course_name = args.course_number.upper().strip()
    vectordb_path = os.path.abspath(vectordb_root)

    if not os.path.exists(vectordb_path):
        print("failed to find vectordb for course %s" % course_name)
        exit(1)
    
    vectorstore = VectorDBReader(db_path=vectordb_path, collection_name=course_name)
else:
    vectorstore = VectorDBReader(db_path=None)

retriever = vectorstore.as_retriever()

rag_chain = chain.make_chain(retriever)

while True:
    print("Enter question: ")
    question = input()

    print("\nAnswer: ")

    my_out = rag_chain.invoke(question)
    print("\n")
    print("===== output =====")
    print(my_out)
    print("\n")
