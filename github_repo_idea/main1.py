import streamlit as st
import os
import re
import textwrap

from dotenv import load_dotenv
from llama_hub.github_repo import GithubClient, GithubRepositoryReader
from llama_index import VectorStoreIndex, download_loader
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import DeepLakeVectorStore

# Load environment variables
load_dotenv()

# Fetch and set API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
active_loop_token = os.getenv("ACTIVELOOP_TOKEN")
dataset_path = os.getenv("DATASET_PATH")

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
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
    query_engine = index.as_query_engine()
    return query_engine

def main():
    st.title("GitHub QA Model")

    # Get GitHub repository URL from user
    github_url = st.text_input("Enter GitHub repository URL")

    if st.button("Submit"):
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
            st.write("Documents uploaded:")
            for doc in docs:
                st.write(doc.metadata)

            query_engine = upload_to_vector_store(docs)

            intro_question = "What is the repository about?"
            st.write(f"Test question: {intro_question}")
            st.write("=" * 50)
            answer = query_engine.query(intro_question)
            st.write(f"Answer: {textwrap.fill(str(answer), 100)}")

            # while True:
            user_question = st.text_input("Please enter your question (or type 'exit' to quit)")
            if user_question.lower() == "exit":
                st.write("Exiting, thanks for chatting!")
                # break

            st.write(f"Your question: {user_question}")
            st.write("=" * 50)

            answer = query_engine.query(user_question)
            st.write(f"Answer: {textwrap.fill(str(answer), 100)}")
        else:
            st.warning("Invalid GitHub URL. Please try again.")

if __name__ == "__main__":
    main()
