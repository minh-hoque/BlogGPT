import streamlit as st

from bloggpt import main


# Initialize state variables
if "topic" not in st.session_state:
    st.session_state.topic = None
if "outline" not in st.session_state:
    st.session_state.outline = None

with st.form("my_form"):
    topic_str = st.text_input("Topic:")

    default_text = """# Header 1
Description of this blog section
    
# Header 2
Description of this blog section
    
# Header 3
Description of this blog section
    """
    st.text_area("Inside the form", value=default_text, height=200)

    # Every form must have a submit button.
    submitted = st.form_submit_button("Generate Blog")
    if submitted:
        # Store in state variables
        st.session_state.topic = topic_str
        st.session_state.outline = default_text
    print("submitted: ", submitted)

if st.session_state.topic and st.session_state.outline:
    st.write("Generating Blog")
    st.write(st.session_state.topic)
    st.write(st.session_state.outline)

    with st.expander("LLM Agent Output"):
        main()
        # st.code(main())
