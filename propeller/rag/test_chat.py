import chain
import sys
import vectordb

from langchain_community.vectorstores import Chroma


input_paths = sys.argv[1:]
if len(input_paths) == 0:
    # test data
    input_paths = ["./rock_parrot.pdf"]
    #print("give input file paths as arguments")
    #exit(1)


print("input: " + str.join(", ", input_paths))


# TODO: need to use create() and series of add_pdf() calls 
vectorstore = vectordb.create_from_file(input_paths[0])
retriever = vectorstore.as_retriever()


rag_chain = chain.make_chain(retriever)

"""
example question: "When was the rock parrot discovered?"
"""
print("Enter question: ")
question = input()

my_out = rag_chain.invoke(question)
print("\n")
print("===== output =====")
print(my_out)
print("\n")

