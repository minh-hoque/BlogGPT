import streamlit as st
from bloggpt import run_bloggpt


# Function to initialize session state
def init_session_state():
    if "topic" not in st.session_state:
        st.session_state.topic = None
    if "outline" not in st.session_state:
        st.session_state.outline = []
    if "num_sections" not in st.session_state:
        st.session_state.num_sections = 1


def get_default_text(section_num):
    return f"""# Header {section_num}
Description of this blog section. Describe important aspects of this blog section.
Search for: (keywords)"""


# Function to create a form
def create_form():
    with st.form("my_form"):
        topic_str = st.text_input("Topic:")
        topic_str = "Topic: " + topic_str

        blog_outline = []
        for i in range(st.session_state.num_sections):
            outline_section = st.text_area(
                f"Define the blog section {i + 1}",
                value=get_default_text(i + 1),
                height=200,
            )
            blog_outline.append(outline_section)

        # Add button to increase the number of blog sections
        cols = st.columns(3)
        with cols[0]:
            if st.form_submit_button("Add new blog section"):
                st.session_state.num_sections += 1
                st.experimental_rerun()
        with cols[1]:
            if st.form_submit_button("Remove last blog section"):
                st.session_state.num_sections -= 1
                st.experimental_rerun()
        with cols[2]:
            # Every form must have a submit button.
            submitted = st.form_submit_button("Generate Blog")

        if submitted:
            # Store in state variables
            st.session_state.topic = topic_str
            st.session_state.outline = "\n\n".join(blog_outline)


# Function to display blog outline
def display_blog_outline():
    if st.session_state.topic and st.session_state.outline:
        with st.expander("Blog Outline"):
            st.write(f"# {st.session_state.topic}")
            st.write(st.session_state.outline)

        try:
            run_bloggpt(
                topic_str=st.session_state.topic, blog_outline=st.session_state.outline
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


# Initialize session state
init_session_state()

# Create form
create_form()

# Display blog outline
display_blog_outline()
