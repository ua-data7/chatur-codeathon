import chain
import sys
from vectordb import VectorDB

from langchain_community.vectorstores import Chroma

input_paths = sys.argv[1:]
if len(input_paths) == 0:
    # test data
    input_paths = ["./rock_parrot.pdf"]
    #print("give input file paths as arguments")
    #exit(1)

"""
example question: "When was the rock parrot discovered?"
"""
vectorstore = VectorDB(None)

for input_path in input_paths:
    print("> input: " + input_path)
    vectorstore.add_file(input_path)

retriever = vectorstore.as_retriever()

rag_chain = chain.make_chain(retriever)
print("Enter question: ")
question = input()

my_out = rag_chain.invoke(question)
print("\n")
print("===== output =====")
print(my_out)
print("\n")
