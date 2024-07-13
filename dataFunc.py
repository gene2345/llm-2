import json
import vecs
import boto3
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_aws import ChatBedrock, BedrockLLM
from langchain_core.prompts import ChatPromptTemplate
import boto3
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers.string import StrOutputParser

load_dotenv()

session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

modelID = "anthropic.claude-3-sonnet-20240229-v1:0"
Bedrock_client = boto3.client("bedrock-runtime", 'us-west-2')

def add_context(sentence, db_name):

    embeddings = []

    # invoke the embeddings model for each sentence
    response = Bedrock_client.invoke_model(
        body= json.dumps({"inputText": sentence}),
        modelId= "amazon.titan-embed-text-v1",
        accept = "application/json",
        contentType = "application/json"
    )
    # collect the embedding from the response
    response_body = json.loads(response["body"].read())
    # add the embedding to the embedding list
    embeddings.append((sentence, response_body.get("embedding"), {}))

    vx = vecs.Client(os.getenv("DB_CONNECTION"))
    sentences = vx.get_or_create_collection(name=db_name, dimension=1536)
    sentences.upsert(records=embeddings)
    sentences.create_index()

def rag_query(query_sentence, db_name, limiter):

    # create vector store client
    vx = vecs.Client(os.getenv("DB_CONNECTION"))

    # create an embedding for the query sentence
    response = Bedrock_client.invoke_model(
            body= json.dumps({"inputText": query_sentence}),
            modelId= "amazon.titan-embed-text-v1",
            accept = "application/json",
            contentType = "application/json"
        )

    response_body = json.loads(response["body"].read())

    query_embedding = response_body.get("embedding")

    sentences = vx.get_or_create_collection(name=db_name, dimension=1536)
    # query the 'sentences' collection for the most similar sentences
    results = sentences.query(
        data=query_embedding,
        limit=limiter,
        include_value = True
    )
    #print the results
    #for result in results:
        #print(db_name, result)

    return results


def add_user_behaviour(sentence):

    embeddings = []

    # invoke the embeddings model for each sentence
    response = Bedrock_client.invoke_model(
        body= json.dumps({"inputText": sentence}),
        modelId= "amazon.titan-embed-text-v1",
        accept = "application/json",
        contentType = "application/json"
    )

    # collect the embedding from the response
    response_body = json.loads(response["body"].read())
    # add the embedding to the embedding list
    embeddings.append((sentence, response_body.get("embedding"), {}))

    vx = vecs.Client(os.getenv("DB_CONNECTION"))
    sentences = vx.get_or_create_collection(name="userBehaviour", dimension=1536)
    sentences.upsert(records=embeddings)
    sentences.create_index()

def llm_ask(question):
    model_kwargs =  { 
    "max_tokens": 512,
    "temperature": 0.0,
    }

    claude_3_client = ChatBedrock(
    client=Bedrock_client,
    model_id=modelID,
    model_kwargs=model_kwargs,
    )

    context = ""
    for items in rag_query(question, "sentences", 3):
        context += items[0]
    
    # Invoke Example
    messages = [
        ("system", "You are an expert on safe and energy efficient car driving practices. The human will provide the past 5 days of their driving statistics and patterns as the input. Please use the statistics to suggest ways they can make their driving more energy efficient / safer. If everything is good, praise the user on their good points. Only give definitive suggestions or praises. I do not need anything else."),
        ("human","{question}"),
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    # chain = prompt | claude_2_client | StrOutputParser()
    chain = prompt | claude_3_client | StrOutputParser()

    # Chain Invoke
    response = chain.invoke({"question": context + question})
    return response

def user_summary(days):
    model_kwargs =  { 
    "max_tokens": 512,
    "temperature": 0.0,
    }

    claude_3_client = ChatBedrock(
    client=Bedrock_client,
    model_id=modelID,
    model_kwargs=model_kwargs,
    )

    # Find recent user behaviour
    list_recent = []
    counter = 5
    for i in range(days):
        if counter == 0:
            break
        else:
            counter -= 1
            dayer = days-i
            list_recent.append(str(dayer))

    question = f"Days recorded: "

    for items in list_recent:
        question+= items*1000

    context = ""
    for items in rag_query(question, "userBehaviour", 5):
        context += items[0]
    print(context)
    messages = [
        ("system", "You are accessing the driving information of a user for the last 5 days. Please generate a summary of each statistic so that it can be further fed into another LLM for further analysis"),
        ("human","{question}"),
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    # chain = prompt | claude_2_client | StrOutputParser()
    chain = prompt | claude_3_client | StrOutputParser()

    # Chain Invoke
    response = chain.invoke({"question": context + question})
    return response

def llm_ask_food(question):
    model_kwargs =  { 
    "max_tokens": 512,
    "temperature": 0.0,
    }

    claude_3_client = ChatBedrock(
    client=Bedrock_client,
    model_id=modelID,
    model_kwargs=model_kwargs,
    )

    context = ""
    for items in rag_query(question, "food", 3):
        context += items[0]
    
    # Invoke Example
    messages = [
        ("system", "You are an expert on food. Focus on where the user has been in the past few days and recommend good food for them"),
        ("human","{question}"),
    ]

    prompt = ChatPromptTemplate.from_messages(messages)

    # chain = prompt | claude_2_client | StrOutputParser()
    chain = prompt | claude_3_client | StrOutputParser()

    # Chain Invoke
    response = chain.invoke({"question": context + question})
    return response