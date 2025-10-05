# streamlit_app.py
import streamlit as st
from middleware import Orchestrator

# Initialize orchestrator
orchestrator = Orchestrator()

def main():
    st.title("AI Tutor Orchestrator")
    st.write("Enter your question or request below:")

    student_prompt = st.text_area("Student Prompt", height=100)

    if st.button("Get Response"):
        if student_prompt.strip() == "":
            st.warning("Please enter a prompt!")
            return

        with st.spinner("Thinking..."):
            out = orchestrator.select_and_run(student_prompt)

        st.success("Response ready!")
        st.write(f"**Chosen Tool:** {out['chosen_tool']}")
        st.write(f"**Payload Used:** {out['payload']}")
        st.write("**Tool Response:**")
        st.json(out['tool_response'])

if __name__ == "__main__":
    main()
