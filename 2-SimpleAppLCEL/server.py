from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from langserve import add_routes
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
model = ChatGroq(model = "llama-3.1-8b-instant", groq_api_key=groq_api_key)

#1. Create Prompt Template
generic_template = "Translate the following into {language}:"
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", generic_template),
        ("human", "{text}")
    ]
)

#2. Create Output Parser
parser = StrOutputParser()

#3.Create the chain
chain = prompt | model | parser

#4. App definition
app = FastAPI(title="Translation App with LCEL and Groq",
              version="0.1",
              description="A simple translation app using LangChain EL and Groq LLM")

# 5. Add the chain as a route
add_routes(
    app,
    chain, 
    path="/chain"
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)