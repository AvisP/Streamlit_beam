"""
### Stable Diffusion on Beam ###

**Deploy it as an API**

beam deploy app.py:generate_image
"""
from beam import App, Runtime, Image, Output, Volume
import base64
import torch
import PIL
from io import BytesIO
from diffusers import StableDiffusionXLPipeline
from diffusers.schedulers import DPMSolverMultistepScheduler
import ollama
import os
import streamlit as st
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
# from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.indices.loading import load_index_from_storage

from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.core.node_parser import get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Document
cache_path = "./models"

# The environment your app runs on
app = App(
    name="RAG-app",
    runtime=Runtime(
        cpu=2,
        memory="32Gi",
        gpu="T4", # T4, A10G
        image=Image(
            python_version="python3.10",
            python_packages="requirements.txt",
            commands=["ollama pull llama2 && import ollama"],
        ),
    ),
    volumes=[Volume(name="models", path="./models")],
)

# This runs once when the container first boots
def load_models():
    loaded_model = "llama2"
    llm = Ollama(model=loaded_model, request_timeout=1200.0)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")

    return embed_model, llm

# Convert Image to Base64 
def im_2_b64(image):
    buff = BytesIO()
    image.save(buff, format="JPEG")
    img_str = base64.b64encode(buff.getvalue())
    return img_str

# Convert Base64 to Image
def b64_2_img(data):
    buff = BytesIO(base64.b64decode(data))
    return PIL.Image.open(buff)

@app.rest_api(
    loader=load_models,
    outputs=[Output(path="output_0.png"),
             Output(path="output_1.png")],
)
def llm_output(**output):
    # Grab inputs passed to the API
    try:
        prompt = inputs["prompt"]
    # Use a default prompt if none is provided
    except KeyError:
        prompt = "a renaissance style photo of elon musk"
    
    # Retrieve pre-loaded model from loader
    embed_model, llm = inputs["context"]

    response = ollama.chat(model='llama2', messages=[
    {
        'role': 'user',
        'content': 'Why is the sky blue?',
    },
    ])
    print(response['message']['content'])
    return response