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
cache_path = "./models"

# The environment your app runs on
app = App(
    name="SDXL-base-app",
    runtime=Runtime(
        cpu=2,
        memory="32Gi",
        gpu="A10G", # T4, A10G
        image=Image(
            python_version="python3.10",
            python_packages=[
                "diffusers[torch]>=0.10",
                "transformers",
                "torch",
                "pillow",
                "accelerate",
                "safetensors",
                "xformers",
                "streamlit"
            ],
            # commands=["pip install streamlit && streamlit run ST_test.py"],
        ),
    ),
    volumes=[Volume(name="models", path="./models")],
)

# This runs once when the container first boots
def load_models():
    base_pipeline = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16)
    base_pipeline = base_pipeline.to("cuda")
    base_pipeline.scheduler = DPMSolverMultistepScheduler.from_config(base_pipeline.scheduler.config)

    # refiner_pipeline = StableDiffusionXLImg2ImgPipeline.from_pretrained("stabilityai/stable-diffusion-xl-refiner-1.0", 
    #                                                                     # text_encoder_2=base_pipeline.text_encoder_2,
    #                                                                     # vae=base_pipeline.vae,
    #                                                                     torch_dtype=torch.float16).to("cuda")
    # refiner_pipeline = []

    return base_pipeline

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
def generate_image(**inputs):
    # Grab inputs passed to the API
    try:
        prompt = inputs["prompt"]
    # Use a default prompt if none is provided
    except KeyError:
        prompt = "a renaissance style photo of elon musk"
    
    # Retrieve pre-loaded model from loader
    base_pipeline = inputs["context"]

    torch.backends.cuda.matmul.allow_tf32 = True

    if int(inputs["seed_input"])>0:
        generator = torch.Generator(device='cuda').manual_seed(int(inputs["seed_input"]))
    else:
        generator = torch.Generator(device='cuda').manual_seed(int(torch.randint(1, 9999, (1,))))
    # generator = torch.Generator(device="cuda")
    print("#####  "+ str(inputs["num_images_per_prompt"]) + "  " + prompt)

    processed_base_pipe = base_pipeline(prompt, 
                                                negative_prompt=inputs["negative_prompt"],
                                                generator=generator,
                                                guidance_scale=inputs["guidance_scale"],
                                                num_images_per_prompt=inputs["num_images_per_prompt"],
                                                num_inference_steps=inputs["num_inference_steps"])

    ENCODING = 'utf-8'
    ret_images ={}

    for i in range(inputs["num_images_per_prompt"]):
        # print(type(processed_base_pipe.images[i]))
        IMAGE_FILE_NAME = "output_"+str(i)+".png"
        print(IMAGE_FILE_NAME)
        print(f"Saved Image: {processed_base_pipe.images[i]}")
        image = processed_base_pipe.images[i]
        image.save(IMAGE_FILE_NAME)
        # first: reading the binary stuff
        # note the 'rb' flag
        # result: bytes
        with open(IMAGE_FILE_NAME, 'rb') as open_file:
            byte_content = open_file.read()

        # second: base64 encode read data
        # result: bytes (again)
        base64_bytes = base64.b64encode(byte_content)

        # third: decode these bytes to text
        # result: string (in utf-8)
        base64_string = base64_bytes.decode(ENCODING)
        # print(base64_string)
        ret_images["b64_image_"+str(i)] = base64_string

    print("Finished processing "+str(inputs["num_images_per_prompt"])+" images")

    return ret_images