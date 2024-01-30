
from langchain.chains import (
    LLMChain,
    ConversationalRetrievalChain
)
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama

from langchain.memory import (
    ConversationBufferMemory
)


# Prompt
prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "Using the following documents, help answer questions as a teacher would help a student. Remember to only answer the question they asked: {context}"
        ),
        HumanMessagePromptTemplate.from_template("{question}"),
    ],
    output_parser=StrOutputParser()
)

# LLM
llm = Ollama(
    model="mistral",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# question from human
def make_chain(retriever):
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt}
    )
