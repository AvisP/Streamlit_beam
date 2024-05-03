import streamlit as st
import requests
import json
import ast
import io
from streamlit_gsheets import GSheetsConnection
import time

headers = {
  "Accept": "*/*",
  "Accept-Encoding": "gzip, deflate",
  "Authorization": "Basic ",
  "Connection": "keep-alive",
  "Content-Type": "application/json"
}

def authenticate(username, password, data):
    if username and password:
        x = data[data.username==username]["password"].values
        if x:
            if str(x[0]) == password:
                return True
            return False
        else:
            st.sidebar.error('Register for username and password')
    else:
        st.sidebar.error('Enter both username or password')
        return False
    
def extract_llm_response(llm_response):
    index = llm_response.rfind("[/INST]")
    return llm_response[index+7:]

def display_messages():
    for msg in st.session_state["chat_history"][1:]:
        print(msg["role"])
        if msg["role"] == "user":
            selected_avatar = "👨‍💻"
        else:
            selected_avatar = "🤖"
        st.chat_message(msg["role"], avatar=selected_avatar).write(msg["content"])

def main():
    try:
        response
    except:
        response=None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history.append({ "role": "user", "content": "You are a friendly chatbot who answers user questions"})
        st.session_state.chat_history.append({"role": "assistant", "content": "Hello! I'm a friendly chatbot here to help answer any questions you may have. What's on your mind today?"})
    
    ENCODING = 'utf-8'
    st.set_page_config(page_title="A Chatbot demo",
                       page_icon=":home:")
    st.sidebar.title('Login')
    username = st.sidebar.text_input('Username')
    password = st.sidebar.text_input('Password', type='password')
    with st.sidebar:
        st.markdown("📝 [Request Access](https://forms.gle/gHMJZkiKi4X9bR5KA)")
    conn = st.experimental_connection("gsheets", type=GSheetsConnection)

    data = conn.read(spreadsheet=st.secrets.connections.gsheets.spreadsheet, ttl=60, usecols=[0, 1])

    if st.sidebar.button('Login'):
        if authenticate(username, password, data):
            st.sidebar.success('Login successful')
            st.session_state['authenticated'] = True
        else:
            st.sidebar.error('Invalid username or password')

    if st.session_state.get('authenticated'):
        st.title('Demo Application for Chatbot on beam')
        hostname = st.secrets.server.url_Mistral
        AUTH_CRED = st.secrets.server.AUTH_CRED
        CLIENT_ID = st.secrets.server.CLIENT_ID
        CLIENT_SECRET = st.secrets.server.CLIENT_SECRET

        with st.sidebar:
            st.sidebar.title("Settings")
            temperature = st.sidebar.slider(
                    "Temperature",
                    min_value=0.01,  # Minimum value
                    max_value=4.0,  # Maximum value
                    value=0.01, # Default value
                    step=0.005  # Step size
                )
            
            max_new_tokens = st.sidebar.slider(
                    "max new tokens",
                    min_value=8,  # Minimum value
                    max_value=4096,  # Maximum value
                    value=256, # Default value
                    step=8  # Step size
                )
            
            max_length = st.sidebar.slider(
                    "max length",
                    min_value=16,  # Minimum value
                    max_value=4096,  # Maximum value
                    value=256, # Default value
                    step=8  # Step size
                )
            
            top_p = st.sidebar.slider(
                    "Top_p",
                    min_value=0.01,  # Minimum value
                    max_value=1.0,  # Maximum value
                    value=0.75, # Default value
                    step=0.005  # Step size
                )
            
            top_k = st.sidebar.slider(
                    "Top_k",
                    min_value=100,  # Minimum value
                    max_value=1,  # Maximum value
                    value=40, # Default value
                    step=1  # Step size
                )
            debug_flag = st.checkbox('Debug prompt history')

        with st.container():
            if st.button("Reset Chat"):
                    st.session_state.chat_history = []
                    st.session_state.chat_history.append({ "role": "user", "content": "You are a friendly chatbot who answers user questions"})
                    st.session_state.chat_history.append({"role": "assistant", "content": "Hello! I'm a friendly chatbot here to help answer any questions you may have. What's on your mind today?"})
                    
            user_query = st.chat_input("Enter your prompt", max_chars=3000)
            display_messages()
            
            if user_query:
                st.chat_message("user", avatar="👨‍💻").write(user_query)
                
                st.session_state.chat_history.append({ "role": "user", "content": user_query})
                if debug_flag:
                    st.write(st.session_state.chat_history)
                payload = {"prompt":st.session_state.chat_history,
                            "temperature":temperature,#0.1,
                            "top_p":top_p,#0.75,
                            "top_k":top_k,#40,
                            "num_beams":4,
                            "max_length":max_length,#256,
                            "max_new_tokens":max_new_tokens#512
                            }
                headers["Authorization"] += AUTH_CRED
                response = requests.request("POST", hostname, 
                                            headers=headers,
                                            # timeout=1200,
                                            data=json.dumps(payload)
                                            )
                
                if response.ok:
                    print(ast.literal_eval(response.content.decode("utf-8"))['task_id'])
                    if response.text:
                        TASK_ID = ast.literal_eval(response.content.decode("utf-8"))['task_id']

                        url_status = f"https://api.beam.cloud/v1/task/{TASK_ID}/status/"
                        # Prepare the headers
                        headers_status = {
                            "Content-Type": "application/json"
                        }

                        # Prepare the authentication
                        auth = (CLIENT_ID, CLIENT_SECRET)
                        current_status  = "PENDING"

                        while(current_status=="PENDING" or current_status=="RUNNING"):
                            response_status = requests.get(url_status, headers=headers_status, auth=auth)

                            # Check if the request was successful (status code 200)
                            if response_status.status_code == 200:
                                # Print the response content
                                print(response_status.json())
                                current_status = response_status.json()["status"]
                                task_id = response_status.json()["task_id"]
                                started_at = response_status.json()["started_at"]
                                if started_at:
                                    st.toast(task_id + " " + str(started_at) + " " + current_status)
                                else:
                                    st.toast(task_id + " " + current_status)
                                time.sleep(5)

                        if response_status.json()["status"]=="COMPLETE":
                            print(response_status.json())
                            data_url = response_status.json()['outputs']['./output.txt']['url']

                            response_data = requests.get(data_url)

                            if response_data.ok:
                                llm_response = response_data.content.decode("utf-8")
                                # llm_response_only = extract_llm_response(llm_response)
                                print(llm_response)
                                st.chat_message("assistant", avatar="🤖").write(llm_response)
                                st.session_state.chat_history.append({ "role": "assistant", "content": llm_response})
                                # chat_history.append(["assisstant":llm_response_only]) 
                            else:
                                print(" Response data error " + response_data)
                else:
                    st.write(response)

        

if __name__ == '__main__':
    main()