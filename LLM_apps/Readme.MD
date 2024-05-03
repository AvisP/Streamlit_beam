In this repo a chatbot application is shown that can be deployed on streamlit community cloud or run locally that communicates via API calls to a server on beam cloud. The beam cloud is running a 8 bit Quantized version of Meta's Llama3 large language model. The application also has an authentication feature that connects to google spread sheets and based on entered username and password, validates login and gives access to using chatbot. Live demo of app running on [Streamlit cloud](https://appbeam-iuiwleburg3j5jvuevkz5q.streamlit.app/)

The streamlit app uses an authentication package [st-gsheets-connection](https://github.com/streamlit/gsheets-connection) to get username and password and use it to retrieve a predefined list of users from a google sheet. Details about how to do the connection can be found [here](https://docs.streamlit.io/knowledge-base/tutorials/databases/private-gsheet)

After successful authentication the chatbot is ready to assist the user. You can ask a question and task request will be initiated on the application running on beam cloud. Using the task_id, the status of the application will be monitored and displayed through a mini-box on the bottom left of the page. Once terminated, the output will be retrieved and displayed to user on the streamlit window. There is a Reset button also to reset the chat.

The `beam_RAG.py` is to be deployed on the beam server and `ST-chatbot.py` is the streamlit application to be deployed on the streamlit community cloud or can be run locally

![Screenshot1](https://i.ibb.co/VMx6RVN/Screenshot-2024-03-25-at-6-06-25-PM.png)

![Screenshot](https://i.ibb.co/kSr5xV3/Screenshot-2024-03-25-at-6-07-21-PM.png)


