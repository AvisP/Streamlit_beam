In this repo an example of a text to image application is shown that can be deployed on streamlit community cloud or run locally that communicates via API calls to a server on beam cloud. The beam cloud is running a base model and refiner model of SDXL. The application also has an authentication feature that connects to google spread sheets and based on entered username and password, validates login and gives access to using SDXL app. Live demo of app running on [Streamlit cloud](https://appbeam-6a9jddgebdzanwmfkff35l.streamlit.app/) 

There are two components to it, first is the text to image component where positive and negaive prompts can be enetered. There are some associated settings on the left on side bar that dicatates the image generation quality and time required. Higher the number of steps better is the image quality and guidance determines if the model should be more creative or just follow the prompts judiciously. A manual seed parameter can be entered for reproducibility. The first part used the base model of SDXL. Images can be saved by right clicking on them.

On the second part is a refiner model, that allows to upload an image and further process it. This part adds more details or improves image quality based on the prompts being entered.

The streamlit app uses an authentication package [st-gsheets-connection](https://github.com/streamlit/gsheets-connection) to get username and password and use it to retrieve a predefined list of users from a google sheet. Details about how to do the connection can be found [here](https://docs.streamlit.io/knowledge-base/tutorials/databases/private-gsheet)  

The GUI code is in `text2image_SDXL.py` and the scripts to be deployed in beam cloud are `beam_example_SDXL_base.py` and `beam_example_SDXL_refiner.py` for base and refiner model respectively.

### Sample screenshots

![Screenshot|150%](https://i.ibb.co/W3ZPngr/Screenshot-2024-03-13-at-1-07-38-AM.png)

![Screenshot 2](https://i.ibb.co/x8rhsYC/Screenshot-2024-03-13-at-2-20-47-AM.png)

![Screenshot 3](https://i.ibb.co/jyy1jw0/Screenshot-2024-03-13-at-2-27-42-AM.png)
