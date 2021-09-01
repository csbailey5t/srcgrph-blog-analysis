import frontmatter
import re
import spacy
import streamlit as st
import textdescriptives as td

from bs4 import BeautifulSoup
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePath


@dataclass
class BlogPost:
    filename: str
    content: str


def get_post_paths(data_dir):
    """
    Takes a directory of markdown files, and returns a list of paths
    """
    root_p = Path(".")
    post_paths = root_p.glob(f"{data_dir}/**/*.md")
    return list(post_paths)


def clean_md_text(md_string):

    # remove fenced code blocks
    # regex from https://stackoverflow.com/questions/64111377/remove-markdown-code-block-from-python-string
    no_codeblocks = re.sub(
        r"^```[^\S\r\n]*[a-z]*(?:\n(?!```$).*)*\n```", "", md_string, 0, re.MULTILINE
    )

    # remove html
    soup = BeautifulSoup(no_codeblocks, "html.parser")
    for el in soup.find_all():
        el.decompose()

    # remove markdown link urls
    no_md_urls = re.sub(r"\(([^)]+)\)", "", soup.text)

    # remove other urls
    no_urls = re.sub(r"http\S+", "", no_md_urls)

    # hackily, directly remove a few particular characters
    clean_text = (
        no_urls.replace("`", "").replace("[", "").replace("]", "").replace("!", "")
    )

    return clean_text


def get_post_data(post_paths):
    """
    Takes a list of filenames, reads contents, returns a list of BlogPost
    """
    posts = []
    for post_path in post_paths:
        post = frontmatter.load(post_path)
        clean_post = clean_md_text(post.content)
        posts.append(BlogPost(post["title"], clean_post))
    return posts


# TODO:
# - organize blogposts by year, so, select year, then post
# - convert \n to a space


def main():
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe("textdescriptives")

    st.header("Sourcegraph blog analysis")

    post_paths = get_post_paths("blogposts")
    # post_data = get_post_data(post_paths)

    # docs = nlp.pipe((blogpost.content for blogpost in post_data))
    # st.write(td.extract_df(docs))

    st.sidebar.header("Select a blog post to analyze")
    selected_post = st.sidebar.selectbox("Post", options=post_paths)

    blog_post = frontmatter.load(selected_post)
    clean_post = clean_md_text(blog_post.content)
    doc = nlp(clean_post)
    st.subheader(blog_post["title"])
    st.write("**Readability stats** - remember to take this with a grain of salt")
    st.write(
        "For info on common readability scores, take a look at [this](https://en.wikipedia.org/wiki/Readability#Popular_readability_formulas)."
    )
    st.write(doc._.readability)
    st.write("**Token count stats **")
    st.write(doc._.counts)

    # Turn this into a three column layout
    # Show most common nouns
    st.write("**10 most common nouns**")
    nouns = [t.text for t in doc if t.pos_ == "NOUN"]
    noun_counter = Counter(nouns)
    st.write(", ".join([word for (word, _) in noun_counter.most_common(10)]))

    # Show most common verbs
    st.write("**10 most common verbs**")
    verbs = [t.text for t in doc if t.pos_ == "VERB"]
    verb_counter = Counter(verbs)
    st.write(", ".join([word for (word, _) in verb_counter.most_common(10)]))

    # Show most common adjectives
    st.write("**10 most common adjectives**")
    adjectives = [t.text for t in doc if t.pos_ == "ADJ"]
    adj_counter = Counter(adjectives)
    st.write(", ".join([word for (word, _) in adj_counter.most_common(10)]))

    st.write("**Post text**")
    st.write(doc)


if __name__ == "__main__":
    main()
