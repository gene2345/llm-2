from dataFunc import add_context
import os
from langchain.text_splitter import NLTKTextSplitter

directory = r'C:\Users\leege\OneDrive\Documents\llm-2\food'
 
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)

    #open file
    f = open(f, "r", encoding='utf-8', errors='ignore')
    data = str(f.read())

    #nltk chunking
    text_splitter = NLTKTextSplitter()
    docs = text_splitter.split_text(data)

    #feed into knowledge vectordb
    for chunks in docs:
        add_context(chunks,"food")

