import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import LLMChain,LLMMathChain
from langchain_core.prompts import PromptTemplate
from langchain.agents.agent_types import AgentType
from langchain.agents import AgentExecutor, initialize_agent, Tool
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.utilities import WikipediaAPIWrapper

#Set up streamlit

st.set_page_config(page_title="Text to Math Problem Solver",page_icon="🐦🔗")
st.title("➕➖✖️➗ Text to Math Problem Solver and Data Search assistant using Google Gemma 2")

st.sidebar.title("Settings")
api_key=st.sidebar.text_input("Enter your Groq api key:",type="password")

if not api_key:
    st.info("Please add your Groq api key to continue")
    st.stop()

llm=ChatGroq(model_name="gemma2-9b-it",groq_api_key=api_key)

wiki=WikipediaAPIWrapper()
wiki_tool=Tool(
    name="Wikipedia",
    func=wiki.run,
    description="Tool for searching the web to find the solutions based on your queries."
)

math_chain=LLMMathChain.from_llm(llm=llm)
calc=Tool(
    name="Calculator",
    func=math_chain.run,
    description="Tool for solving your math based queries. Only math expressions are allowed."
)


template='''
 You are a agent tasked to solve the mathematical question. Logically arrive at the solution by providing detailed explanation
 and display it point wise for the question below.
 QUESTION: {question}
 ANSWER: 
'''
prompt=PromptTemplate(
    input_variables=["QUESTION"],
    template=template
)

#Combine all tools to chain

chain=LLMChain(llm=llm,prompt=prompt)

reasoning_tool=Tool(
    name="Reasoning Tool",
    func=chain.run,
    description="A tool for answering logic-based and reasoning questions"
)

assistant_agent=initialize_agent(tools=[wiki_tool,calc,reasoning_tool],llm=llm,agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,verbose=False,handle_parsing_errors=True)


if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role":"assistant","content":"Hi, I am a Math Assistant who can answer all your math problems!"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

question=st.text_area("Enter your Question ?")

if st.button("Find my answer"):
    if question:
        with st.spinner("Generating Response...."):
            st.session_state.messages.append({"role":"user","content":question})
            st.chat_message("user").write(question)

            st_cb=StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
            response=assistant_agent.run( st.session_state.messages,callbacks=[st_cb])

            st.session_state.messages.append({"role":"assistant","content":response})
            st.write("### Response ###:")
            st.success(response)

    else:
        st.warning("Please enter your question!!")