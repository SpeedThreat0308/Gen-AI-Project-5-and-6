import os
from dotenv import load_dotenv
import streamlit as st
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentType, initialize_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import mysql.connector
from langchain_groq import ChatGroq

st.set_page_config(page_title="Langchain Chat with SQL DB", page_icon="🐦🔗")
st.title("🐦🔗 Langchain Chat using SQL DB")

MYSQL="USE_MYSQL"

db_uri=None


st.sidebar.title("Settings")
clicked_check=st.sidebar.checkbox(label="Select the Database to Work with the model",value="Connect to your SQL Database")

if clicked_check:
    db_uri=MYSQL
    mysql_host=st.sidebar.text_input("Enter you localhost name")
    mysql_user=st.sidebar.text_input("Enter your username")
    mysql_password=st.sidebar.text_input("Enter your password",type="password")
    mysql_db=st.sidebar.text_input("Enter the database name")
else:
    st.info("Please select your db to continue!")

api_key=st.sidebar.text_input("Enter your Groq API Key:",type="password")

if not db_uri:
    st.info("Please enter database info and uri")

if not api_key:
    st.info("Please add groq api key!")
    st.stop()


llm=ChatGroq(model_name="gemma2-9b-it",groq_api_key=api_key,streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_uri==MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide the correct MySQL details")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{quote_plus(mysql_password)}@{mysql_host}/{mysql_db}"))

if db_uri==MYSQL:
    db=configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)

toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(llm,toolkit=toolkit,agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,verbose=True)

if "messages" not in st.session_state or st.sidebar.button("Clear Message History"):
    st.session_state["messages"]=[{"role":"assistant","content":"How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_callbacks=StreamlitCallbackHandler(st.container())
        response=agent.run(user_query,callbacks=[st_callbacks])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)