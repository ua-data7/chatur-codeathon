import os
import chain
import argparse
from vectordb import VectorDB

vectordb_root = "./vectordb"


parser = argparse.ArgumentParser(
    prog='test_chat',
    description='Chat about course materials')

parser.add_argument('course_number', help='course number')
args = parser.parse_args()

course_name = args.course_number.upper().strip()
vectordb_path = os.path.join(vectordb_root, course_name)

if not os.path.exists(vectordb_path):
    print("failed to find vectordb for course %s" % course_name)
    exit(1)

vectorstore = VectorDB(vectordb_path)
retriever = vectorstore.as_retriever()

rag_chain = chain.make_chain(retriever)
print("Enter question: ")
question = input()

print("\nAnswer: ")

my_out = rag_chain.invoke(question)
print("\n")
print("===== output =====")
print(my_out)
print("\n")
