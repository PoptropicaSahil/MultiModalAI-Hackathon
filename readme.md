### Chat with a github Repo! 😁😁

GitHub repos are often overwhelming! Even the best in the business take a while to understand what hundreds of different files really do!
Utilize out tool to understand GitHub repos efficiently. You can ask for summaries, code reviews, comment additions, explanations, pseudocode and a whole lot more!


**Know only python but find it difficult to understand Javascript? Our model is at your rescue! Be it any code in  python, typescript, javascript - dont worry! Markdown files or even pdfs - we support it all!!!**

✔✔Implemented with Llama Index, StreamLit and OpenAI.✔✔

🤞🤞To use, follow the steps:🤞🤞
1) Open a suitable IDE
2) In the .env file, enter the required API keys.
3) Open terminal and go to the directory containing the files.
4) Create virtual environment by running `python3 -m venv venv`
5) Activate it by running `source venv/bin/activate`
6) Move to the code directory `cd github_repo_idea`
7) Install dependencies in  `pip install -r requirements.txt`
8) Run the file! `streamlit run main.py`

Made by Aditri, Arya and Sahil

🎉🎉 How it works 🎉🎉
- We use `llamaindex` with `gpt-3.5-turbo`
- The data fetched from the github repo is indexed and stored using `Activeloop` in `DeepLake` data buckets.
- A `streamlit` UI is spinned up for easy interaction

⚠ Note 
- The landing page of the streamlit UI might show an `UnboundLocalError`. However, the app remains completely functional - simply enter the github repo url and chat with it!
- The API Keys in the .env file will be automatically terminated in a week.