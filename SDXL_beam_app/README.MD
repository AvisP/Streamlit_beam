In this repo an example of a text to image application is shown that can be deployed on streamlit community cloud or run locally that communicates via API calls to a server on beam cloud. The beam cloud is running a base model and refiner model of SDXL. The application also has an authentication feature that connects to google spread sheets and based on entered username and password, validates login and gives access to using SDXL app

There are two components to it, first is the text to image component where positive and negaive prompts can be enetered. There are some associated settings on the left on side bar that dicatates the image generation quality and time required. Higher the number of steps better is the image quality and guidance determines if the model should be more creative or just follow the prompts judiciously. A manual seed parameter can be entered for reproducibility. The first part used the base model of SDXL. Images can be saved by right clicking on them.

On the second part is a refiner model, that allows to upload an image and further process it. This part adds more details or improves image quality based on the prompts being entered.


![Screenshot](https://i.ibb.co/W3ZPngr/Screenshot-2024-03-13-at-1-07-38-AM.png==250x250)
