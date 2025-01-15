# app.py

import os
import logging
import pandas as pd
import streamlit as st
import tempfile 

from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)
from typing import Any
# Import all FunctionDeclarations
from functions import (
    get_daily_detail_data,
    generate_brand_health_overview,
    generate_top_post_details,
    generate_channel_details,
    generate_brand_sentiment_details,
    generate_label_details,
    # Add other FunctionDeclarations here
)
from functions import format_social_listening_data
# Define Tools and Handlers based on interaction_found
from functions.functiondeclarations import (
    brand_health_overview,
    get_top_post_details,
    get_channel_detail,
    get_brand_sentiment_detail,
    get_label_details,
    get_daily_detail,
    # Import other FunctionDeclarations as needed
)
# ============================
# Configure Logging
# ============================
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ============================
# Initialize Data and Tools
# ============================
st.set_page_config(page_title="Insight Chatbot", page_icon="💬")

# Define the base directory and default file paths
base_dir = os.path.dirname(__file__)
default_file_1 = os.path.join(base_dir, "Central Retail and Competitors.xlsx")
default_file_2 = os.path.join(base_dir, "PNJ Campaign.xlsx")

# Function to load data from an Excel file
def loaddata(df_path):
    df = pd.read_excel(df_path, sheet_name="Data")
    df['PublishedDate'] = pd.to_datetime(df['PublishedDate']).dt.date
    return df

# Sidebar for file upload and instructions
with st.sidebar:

    # Dropdown to select a default file
    default_file_option = st.selectbox(
        "Select a sample file:",
        options=["PNJ Campaign.xlsx", "Central Retail and Competitors.xlsx"]
    )
    
    # File uploader for custom Excel files
    uploaded_file = st.file_uploader("Or upload your own Excel file", type=["xlsx"])
    
    st.markdown("### Instructions")  # Use a header to group content
    st.markdown("""
    1. **Data Requirements**:
       - The data must be in the sheet named **'Data'**, containing all basic columns of CMS excel file exported and interaction columns.
       - It is recommended to include the **'Labels1'** column.
    
    2. **Language**:
       - Works best with questions written in **English**.
    
    3. **Question Guidelines**:
       - Please provide **concise** questions for faster responses.
       - For **in-depth** questions, responses may take up to **2 minutes**.
    """)
# Determine which default file to use based on user selection
selected_default_file = (
    default_file_1 if default_file_option == "Central Retail and Competitors.xlsx" else default_file_2
)
# Demo video
with st.expander("Watch the demo video"):
    video_file = open("Demo chatbot.mp4", "rb")
    video_bytes = video_file.read()
    st.video(video_bytes)

# Try to read the file
try:
    if uploaded_file:
        # If the user uploaded a file, read it
        df = loaddata(uploaded_file) 
        file_name = uploaded_file.name  # Get the name of the uploaded file
        st.success(f"Your file '{file_name}' has been uploaded successfully!")
    else:
        # Use the selected default file if no file is uploaded
        df = loaddata(selected_default_file)
        file_name = os.path.basename(selected_default_file)  # Get the name of the selected file
        st.info(f"Using the default file: '{file_name}'.")

    # Format the data
    df, interaction_found, labels1_found = format_social_listening_data(df)

except Exception as e:
    st.error(f"Failed to read the Excel file. Please check the file and try again.")
    st.stop()

    
# @st.cache_data
# def send_chat_message(prompt):
#     prompt += """
#     You are a social listening insight, give me the insight which is from information that you learn from the function responses
#     """

#     # Send a chat message to the Gemini API
#     response = chat.send_message(prompt)

#     # Handle cases with multiple chained function calls
#     function_calling_in_process = True
#     while function_calling_in_process:
#         function_call = response.candidates[0].content.parts[0].function_call

#         # If there's no function call, stop trying to handle function calls
#         if not function_call:
#             function_calling_in_process = False
#             break

#         # Check for a function call or a natural language response
#         if function_call and function_call.name in function_handler.keys():
#             function_name = function_call.name
#             params = {key: value for key, value in function_call.args.items()}
            
#             # Execute the handler on your existing DataFrame
#             function_result = function_handler[function_name](params)

#             # Return that result back to the LLM as a function response
#             response = chat.send_message(
#                 Part.from_function_response(
#                     name=function_name,
#                     response={"content": function_result},
       
#                 )
#             )
#         else:
#             function_calling_in_process = False

#     # Show the final natural language summary
#     return(response.text.replace("$", "\\$"))



def send_chat_message(prompt):
    """
    Send the user's prompt to the LLM, handle function calls in a loop,
    then return the final textual response. All outputs are shown in Streamlit.
    """
    prompt += """
    You are a social listening insight, give me the insight which is from information that you learn from the function responses
    """

    # Ensure there's a chat session in st.session_state
    if "chat_session" not in st.session_state:
        # Initialize or re-initialize your model and chat
        # (You can do this outside or keep it here if you'd like it flexible)
        st.error("Chat session not found in session_state. Please initialize first.")
        return ""

    chat_session = st.session_state.chat_session

    # Optional: You can append instructions to the prompt if desired
    # e.g. a system/role message, etc.
    # prompt += """
    # You are a social listening insight...
    # """

    # 1. Send the user's message to the LLM
    response = chat_session.send_message(prompt)

    # 2. Handle multiple function calls, if any
    while True:
        # Safely check if there's a function call
        function_call = None
        # Make sure we have a candidate with parts
        if (response.candidates 
            and response.candidates[0].content
            and response.candidates[0].content.parts):
            function_call = response.candidates[0].content.parts[0].function_call

        # If no function call is present, break
        if not function_call:
            break

        # If the model wants to call a known function, handle it
        if function_call.name in function_handler:
            function_name = function_call.name
            # Convert the function call arguments into a Python dict
            params = {key: value for key, value in function_call.args.items()}

            # Execute the local Python function
            function_result = function_handler[function_name](params)

            # Send that result back to the LLM as a function response
            response = chat_session.send_message(
                Part.from_function_response(
                    name=function_name,
                    response={"content": function_result},
                )
            )
        else:
            # The LLM requested an unknown function or something else
            st.warning(f"Unknown function call requested: {function_call.name}")
            break

    # 3. Attempt to get final text. If the model only produced function calls, 
    #    .text might raise a ValueError.
    try:
        final_text = response.text
    except ValueError:
        final_text = "No final text was provided. The model returned only a function call."

    # 5. Return the text if you'd like to use it elsewhere
    return final_text

# Display the file name if needed
st.write(f"Currently loaded file: **{file_name}**")



# Create a list of FunctionDeclarations based on interaction_found
if interaction_found:

    company_insights_tool = Tool(
        function_declarations=[
            get_daily_detail,
            brand_health_overview,
            get_top_post_details,
            get_channel_detail,
            get_brand_sentiment_detail,
            get_label_details
        ],
    )
    function_handler = {
    "get_daily_detail": lambda p: get_daily_detail_data(df, p),
    "brand_health_overview": lambda p: generate_brand_health_overview(df, p),
    "get_top_post_details": lambda p: generate_top_post_details(df, p),
    "get_channel_detail": lambda p: generate_channel_details(df, p),
    "get_brand_sentiment_detail": lambda p: generate_brand_sentiment_details(df, p),
    "get_label_details": lambda p: generate_label_details(df, p),
    }
else:
    company_insights_tool = Tool(
        function_declarations=[
            get_daily_detail,
            brand_health_overview,
            get_top_post_details,
            get_channel_detail,
            get_brand_sentiment_detail
        ],
    )
    function_handler = {
    "get_daily_detail": lambda p: get_daily_detail_data(df, p),
    "brand_health_overview": lambda p: generate_brand_health_overview(df, p),
    "get_top_post_details": lambda p: generate_top_post_details(df, p),
    "get_channel_detail": lambda p: generate_channel_details(df, p),
    "get_brand_sentiment_detail": lambda p: generate_brand_sentiment_details(df, p),
    }

# Map function names to their handlers

# ============================
# Initialize Vertex AI
# ============================

PROJECT_ID = "hybrid-autonomy-445719-q2"
import tempfile
import json

# Example: Retrieve credentials from Streamlit secrets
credentials_str = st.secrets["google"]["credentials"]
credentials_dict = json.loads(credentials_str)

# Create a temporary file
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
    json.dump(credentials_dict, temp_file)  # Write JSON to the file
    temp_file_name = temp_file.name


# Set the environment variable to the file path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_name

# Initialize Vertex AI
try:
    import vertexai
    vertexai.init(project=PROJECT_ID)
    # Access the credentials from Streamlit secrets

except Exception as e:
    logger.error(f"Error initializing Vertex AI: {e}")
    st.error("Failed to initialize Vertex AI. Please check your configuration.")
    st.stop()

# Initialize Generative Model
try:
    gemini_model = GenerativeModel(
        "gemini-1.5-pro-002",
        generation_config=GenerationConfig(temperature=0),
        tools=[company_insights_tool],
    )
except Exception as e:
    logger.error(f"Error initializing Generative Model: {e}")
    st.error("Failed to initialize the generative model.")
    st.stop()
try:
    chat = gemini_model.start_chat()
except Exception as e:
    logger.error(f"Error starting chat session: {e}")
    st.error("Failed to start chat session.")
    st.stop()
if "chat_session" not in st.session_state:
    st.session_state.chat_session = gemini_model.start_chat()
# ============================
# Streamlit App Layout
# ============================


st.title("💬 Social Listening Insights Chatbot")

st.markdown("""
Welcome to the **Social Listening Insights Chatbot**! Ask me about your brand's social media performance, channel / sentiment analysis, and more.
""")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input("How's performances of brands on social media?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Ensure send_chat_message returns a string
        response_text = send_chat_message(prompt)
        full_response += response_text
        message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
