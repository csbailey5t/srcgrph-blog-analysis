import frontmatter
import spacy
import streamlit as st
import textdescriptives as td

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


def get_post_data(post_paths):
    """
    Takes a list of filenames, reads contents, returns a list of BlogPost
    """
    posts = []
    for post_path in post_paths:
        post = frontmatter.load(post_path)
        posts.append(BlogPost(post["title"], post.content))
    return posts


# TODO:
# - organize blogposts by year, so, select year, then post
# - remove html from post content
# - remove code blocks
# - convert \n to a space


def main():
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe("textdescriptives")

    st.header("Sourcegraph blog analysis")

    post_paths = get_post_paths("blogposts")
    post_data = get_post_data(post_paths)

    docs = nlp.pipe((blogpost.content for blogpost in post_data))
    st.write(td.extract_df(docs))

    st.sidebar.header("Select a blog post to analyze")
    st.sidebar.selectbox("Post", options=post_paths)
    # st.sidebar.write(fns)


if __name__ == "__main__":
    main()
