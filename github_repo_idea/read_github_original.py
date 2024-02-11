import os
import re

import openai
import streamlit as st
from dotenv import load_dotenv
from llama_hub.github_repo import GithubClient, GithubRepositoryReader
from llama_index import ServiceContext, VectorStoreIndex, download_loader
from llama_index.llms import OpenAI
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import DeepLakeVectorStore

load_dotenv()

# Fetch and set API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
active_loop_token = os.getenv("ACTIVELOOP_TOKEN")
dataset_path = os.getenv("DATASET_PATH")


st.set_page_config(
    page_title="Chat with the Streamlit docs, powered by LlamaIndex",
    page_icon="🦙",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)
openai.api_key = "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"
st.title("Chat about any Github repository, powered by LlamaIndex 💬🦙")
st.info(
    "Made by Aditri, Sahil and Arya",
    icon="📃",
)

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me a question about the Github Repo!",
        }
    ]

#### GET GITHUB URL FROM USER ####


def parse_github_url(url):
    pattern = r"https://github\.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)
    return match.groups() if match else (None, None)


def validate_owner_repo(owner, repo):
    return bool(owner) and bool(repo)


def initialize_github_client():
    github_token = os.getenv("GITHUB_TOKEN")
    return GithubClient(github_token)


def upload_to_vector_store(docs):
    vector_store = DeepLakeVectorStore(
        dataset_path=dataset_path,
        overwrite=True,
        runtime={"tensor_db": True},
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(
        llm=OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.5,
            system_prompt="You are an expert in Python and github libraries. You can understand code and your job is to answer technical questions. Assume that all questions are related to the repository information provided. Keep your answers technical and based on facts – do not hallucinate features.",
        )
    )
    index = VectorStoreIndex.from_documents(
        docs, storage_context=storage_context, service_context=service_context
    )
    # query_engine = index.as_query_engine()
    return index


github_url = st.text_input("Enter GitHub repository URL")


@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(
        text="Loading and indexing the GitHub repo – hang tight! This should take 1-2 minutes."
    ):
        # if st.button("Submit"):
        owner, repo = parse_github_url(github_url)
        if validate_owner_repo(owner, repo):
            github_client = initialize_github_client()
            download_loader("GithubRepositoryReader")
            loader = GithubRepositoryReader(
                github_client,
                owner=owner,
                repo=repo,
                filter_file_extensions=(
                    [".py", ".js", ".ts", ".md"],
                    GithubRepositoryReader.FilterType.INCLUDE,
                ),
                verbose=False,
                concurrent_requests=5,
            )
            st.write(f"Loading {repo} repository by {owner}")
            try:
                docs = loader.load_data(branch="main")
            except:
                docs = loader.load_data(branch="master")
            # finally:
            #     st.write("the repo does not have a main or master branch")
            #     exit()

            st.write("Documents uploaded:")
            for doc in docs:
                st.write(doc.metadata)

            index = upload_to_vector_store(docs)
        return index


# @st.cache_resource(show_spinner=False)
# def load_data():
#     with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
#         reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
#         docs = reader.load_data()
#         service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features."))
#         index = VectorStoreIndex.from_documents(docs, service_context=service_context)
#         return index

index = load_data()

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True
    )

if prompt := st.chat_input(
    "Your question"
):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)  # Add response to message history
