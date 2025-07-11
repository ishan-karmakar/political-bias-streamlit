# Political Bias Model
This is a project that aims to analyze news posts from a social media source (in this case Reddit), and identify the political alignment of them in order to identify trends.

# Example Result
The Streamlit app is available [here](https://ishan-karmakar-streamlit-llm-reader-jbqbat.streamlit.app/).
![Streamlit App Picture](example.png)

# Technologies
This project is made with Python, and uses the [PRAW](https://github.com/praw-dev/praw) API to get the news posts from r/news. To identify the political alignment, the project interfaces with a [Political Bias Model](https://huggingface.co/matous-volf/political-leaning-politics). The submission information and political bias is stored in a file that is used by the Streamlit website later.

# How to Use
## Collecting new data
```bash
$ python3 main.py
```

## Running the Streamlit app
```bash
$ python3 -m streamlit run reader.py
```
