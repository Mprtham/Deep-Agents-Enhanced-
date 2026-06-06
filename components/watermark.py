import streamlit as st


def inject_watermark():
    st.markdown(
        '<div class="watermark">Made by Prathamesh Mishra</div>',
        unsafe_allow_html=True,
    )
