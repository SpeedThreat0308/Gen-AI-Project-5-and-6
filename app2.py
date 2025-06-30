import os
from dotenv import load_dotenv
import validators
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeAudioLoader, YoutubeLoader, UnstructuredURLLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import OpenAIWhisperParser



#streamlit
st.set_page_config(page_title="Langchain:YT&webPage Summarizer",page_icon="🐦🔗")
st.title("🐦🔗 Langchain: Summarize content from your favorite youtube videos or any websites too!")

st.subheader("Summarize URL")

with st.sidebar:
    api_key=st.text_input("Enter your Groq API Key:",type="password")

llm=ChatGroq(model_name="gemma2-9b-it",groq_api_key=api_key)


gen_template='''
  Please provide summary of the following content in 350 words
  Content: {text}
'''
prompt=PromptTemplate(input_variables=["text"],template=gen_template,verbose=True)

url=st.text_input("URL",label_visibility="collapsed")

if st.button("Summarize the content!"):
    if not api_key.strip() or not url.strip():
        st.error("Please Provide the information to continue!")
    
    elif not validators.url(url):
        st.error("Please provide a valid YT or Web Page URL!")

    else:
        try:
            with st.spinner("Waiting...."):
                if "youtube.com" in url or "youtu.be" in url:
                    yt_loader = YoutubeAudioLoader([url], save_dir="genaiproj3")
                    whisper_parser = OpenAIWhisperParser()
                    loader = GenericLoader(yt_loader, whisper_parser)
                else:
                    loader=UnstructuredURLLoader(urls=[url],ssl_verify=True,headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"})
                
                data=loader.load()

                if not data or not data[0].page_content.strip():
                     st.error("Failed to load meaningful content from the YouTube video. It may have no captions, be restricted, or loading failed.")
                     st.stop()
                else:
                    st.info(f"Content size: {len(data[0].page_content)} characters loaded from video.")

                chain=load_summarize_chain(llm,prompt=prompt,chain_type="stuff",verbose=True)
                output_summary=chain.run(data)

                st.success(output_summary)
        except Exception as e:
            st.error(f"Exception: {e}")

