import streamlit as st
from streamlit_chat import message
from utils.load_config import LoadConfig
from utils.app_utils import Apputils
from utils.web_search import WebSearch

APPCFG = LoadConfig()


st.set_page_config(
    page_title="WebLLAMA",
    layout="wide"
)

st.markdown("<h1 style='text-align: center;'>WebGPT</h1>",
            unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []

counter_placeholder = st.sidebar.empty()
st.sidebar.title(
    "WebLLAMA: Llama llm agent with access to the internet")
model_name = st.sidebar.radio("Choose a model:", ("Llama3-8b", "Llama3-70b"))
clear_button = st.sidebar.button("Clear Conversation", key="clear")

if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['model_name'] = []
    st.session_state['chat_history'] = []

response_container = st.container()
container = st.container()
container.markdown("""
    <style>
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 10px;
            background-color: #f5f5f5;
            border-top: 1px solid #ddd;
        }
    </style>
""", unsafe_allow_html=True)

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input')
        submit_button = st.form_submit_button(label='Submit')

    if submit_button and user_input:
        chat_history = f"# Chat history:\n{st.session_state['chat_history'][-2:]}\n\n"
        query = f"# User new question:\n {user_input}"
        messages = [
            {"role": "system", "content": str(
                APPCFG.llm_function_caller_system_role)},
            {"role": "user", "content": chat_history + query}
        ]
        # tools = WebSearch.list_methods()
        instance = WebSearch()
        first_llm_response = Apputils.ask_llm_function_caller(
            gpt_model=APPCFG.gpt_model, temperature=APPCFG.temperature, messages=messages, function_json_list=WebSearch.list_methods(instance))
        st.session_state['past'].append(user_input)
        if first_llm_response is not None:
            # try:
            print("Called function:",
                    first_llm_response.tool_calls[0]['name'])
            web_search_result = Apputils.execute_json_function(
                first_llm_response)
            web_search_results = f"\n\n# Web search results:\n{str(web_search_result)}"
            messages = [
                {"role": "system", "content": APPCFG.llm_system_role},
                {"role": "user", "content": chat_history +
                    web_search_results + query}
            ]
            print(messages)
            print(web_search_results)
            second_llm_response = Apputils.ask_llm_chatbot(
                APPCFG.gpt_model, APPCFG.temperature, messages)
            st.session_state['generated'].append(
                second_llm_response.content)
            chat_history = (
                f"## User query: {user_input}", f"## Response: {second_llm_response.content}")
            st.session_state['chat_history'].append(chat_history)
            # except Exception as e:
            #     print(e)
            #     st.session_state['generated'].append(
            #         "An error occured with the function calling, please try again later.")
            #     chat_history = str(
            #         (f"User query: {user_input}", f"Response: An error occured with function calling, please try again later."))
            #     st.session_state['chat_history'].append(chat_history)
        else:
            try:
                chat_history = str(
                    (f"User query: {user_input}", f"Response: {first_llm_response.content}"))
                st.session_state['chat_history'].append(chat_history)
                st.session_state['generated'].append(
                    first_llm_response.content)
            except:
                st.session_state['generated'].append(
                    "An error occured, please try again later.")
                chat_history = str(
                    (f"User query: {user_input}", f"Response: An error occured, please try again later."))
                st.session_state['chat_history'].append(chat_history)
    

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i],
                    is_user=True,
                    key=str(i) + '_user',
                    # avatar_style=str(here("images/openai.png"))
                    )
            message(st.session_state["generated"][i],
                    key=str(i),
                    # avatar_style=str(here("images/AI_RT.png")),
                    )