import streamlit as st

from bloggpt import main

# Initialize state variables
if "topic" not in st.session_state:
    st.session_state.topic = None
if "outline" not in st.session_state:
    st.session_state.outline = None

with st.form("my_form"):
    topic_str = st.text_input("Topic:")
    topic_str = "Topic: " + topic_str

    default_text = """# Header 1
Description of this blog section. Describe important aspects of this blog section.
Search for: (keywords)
    
# Header 2
Description of this blog section. Describe important aspects of this blog section.
Search for: (keywords)
    
# Header 3
Description of this blog section. Describe important aspects of this blog section.
Search for: (keywords)
    """

    blog_outline = st.text_area(
        "Define the blog outline", value=default_text, height=400
    )

    # Every form must have a submit button.
    submitted = st.form_submit_button("Generate Blog")
    if submitted:
        # Store in state variables
        st.session_state.topic = topic_str
        st.session_state.outline = blog_outline

if st.session_state.topic and st.session_state.outline:
    with st.expander("Blog Outline"):
        st.write(f"# {st.session_state.topic}")
        st.write(st.session_state.outline)

    main(topic_str=topic_str, blog_outline=blog_outline)
