from datetime import datetime
import streamlit as st


st.set_page_config(
    page_title="Explore Streamlit",
)

st.markdown(
    """
    <style>
    /* Apply CSS to all container divs to disable scroll */
    div[data-testid="stVerticalBlock"] > div {
        overflow: hidden; /* Disable scrolling */
        max-height: 100%; /* Ensure content doesn't overflow */
    }
    </style>
    """,
    unsafe_allow_html=True
)


cols = st.columns([1, 3, 2, 2, 2])


# Create Headers
container = cols[0].container(height=60, border=False)
container.markdown(
    """
    <style>
        div[data-testid="checkbox"]
        {
            align-self: flex-end;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)
container.checkbox("Select all", key="select_all", label_visibility="hidden")

container = cols[1].container(height=60, border=False)
container.markdown("#### Name")

container = cols[2].container(height=60, border=False)
container.markdown("#### Type")

container = cols[3].container(height=60, border=False)
container.markdown("#### Size")

container = cols[4].container(height=60, border=False)
container.markdown("#### Time")



# Create first data row
data_container = cols[0].container(height=50, border=False)
data_container.checkbox("webapp_contract.pdf", key="webapp_contract.pdf", label_visibility="hidden")

data_container = cols[1].container(height=50, border=False)
data_container.markdown("webapp_contract.pdf")

data_container = cols[2].container(height=50, border=False)
data_container.markdown("application/pdf")

data_container = cols[3].container(height=50, border=False)
data_container.markdown("23.45 KB")

data_container = cols[4].container(height=50, border=False)
data_container.markdown(datetime(2023, 3, 1).strftime("%b %d, %Y"))


# Create the second data row
data_container = cols[0].container(height=50, border=False)
data_container.checkbox("painting_contract.pdf", key="painting_contract.pdf", label_visibility="hidden")

data_container = cols[1].container(height=50, border=False)
data_container.markdown("painting_contract.pdf")

data_container = cols[2].container(height=50, border=False)
data_container.markdown("application/pdf")

data_container = cols[3].container(height=50, border=False)
data_container.markdown("921.64 KB")

data_container = cols[4].container(height=50, border=False)
data_container.markdown(datetime(2022, 8, 28).strftime("%b %d, %Y"))




