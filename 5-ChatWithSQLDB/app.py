import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
# from langchain.agents import agent_types
# AgentType = agent_types.AgentType

from langchain_groq import ChatGroq


# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="Chat with SQL DB", page_icon=":robot:")
st.title("🤖 Chat with SQL Database")

# Database options
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use Local SQLite DB", "Use MySQL DB"]
selected_db = st.radio("Select Database Option", radio_opt)

# Collect MySQL details if selected
if radio_opt.index(selected_db) == 1:
    db_url = MYSQL
    mysql_host = st.sidebar.text_input("MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database Name")
else:
    db_url = LOCALDB

# Groq API Key
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
if not api_key:
    st.info("Please enter your Groq API key to proceed.")
    st.stop()

# ------------------- LLM Setup -------------------
llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant", streaming=True)

# ------------------- Database Configuration -------------------
@st.cache_resource(ttl=7200)  # cache for 2 hours
def configure_db(db_url, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_url == LOCALDB:
        dbfilepath = (Path(__file__).parent / "db" / "student.db").absolute()
        st.write(f"📁 Using local SQLite DB at: {dbfilepath}")
        engine = create_engine(f"sqlite:///{dbfilepath}")
        return SQLDatabase(engine)
    elif db_url == MYSQL:
        if not all([mysql_host, mysql_user, mysql_password, mysql_db]):
            st.error("Please provide all MySQL connection details in the sidebar.")
            st.stop()
        engine = create_engine(
            f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
        )
        return SQLDatabase(engine)

# Initialize DB
if db_url == MYSQL:
    db = configure_db(db_url, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_url)


## TooL KIT

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type="zero-shot-react-description",
)


if "messages" not in st.session_state or st.sidebar.button("Clear Conversation"):
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask a question about the students database...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(
            user_input,
            callbacks=[streamlit_callback],
        )
        st.session_state.messages.append({"role": "assistant", "content": response})