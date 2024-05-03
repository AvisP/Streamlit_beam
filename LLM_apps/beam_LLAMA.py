from beam import App, Runtime, Image, Output, Volume, VolumeType
from pathlib import Path
import os
import torch
from transformers import (
    GenerationConfig,
    AutoModelForCausalLM, 
    AutoTokenizer,
    BitsAndBytesConfig
)
import time
# Cached model
cache_path = "./models"

# base_model = "mistralai/Mistral-7B-v0.1"
base_model = "meta-llama/Meta-Llama-3-8B-Instruct"

app = App(
    name="llama2",
    runtime=Runtime(
        cpu=2,
        memory="32Gi",
        gpu="T4",
        image=Image(
            python_packages=[
                "accelerate",
                "transformers",
                "torch",
                "sentencepiece",
                "bitsandbytes",
            ],
            # commands=["apt-get update && pip install beautifulsoup4"],
        ),
    ),
    volumes=[
        Volume(
            name="model_weights",
            path=cache_path,
            volume_type=VolumeType.Persistent,
        )
    ],
)

# This runs once when the container first boots
def load_models():
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
    )

    model = AutoModelForCausalLM.from_pretrained(model_id, 
                                                 quantization_config=quantization_config,
                                                 device_map="auto",
                                                #  torch_dtype=torch.float16,
                                                 cache_dir=cache_path,
                                                 token=os.environ["HUGGINGFACE_API_KEY"])
    tokenizer = AutoTokenizer.from_pretrained(model_id, 
                                              device_map="auto",
                                              cache_dir=cache_path,
                                              token=os.environ["HUGGINGFACE_API_KEY"])

    return model, tokenizer

Path("generated_images").mkdir(parents=True, exist_ok=True) 

# @app.rest_api(
#     loader=load_models,
#     timeout=1200,
#     outputs=[Output(path="output.txt")],
# )
@app.task_queue(
    loader=load_models,
    # timeout=1200,
    outputs=[Output(path="output.txt"),
             Output(path="ExecutionTime.txt")
             ],
)
def generate(**inputs):
    input_text = inputs["prompt"]
    # prompt = f"""<s>[INST]{input_text}[/INST]"""
    # prompt = input_text
    
    model, tokenizer = inputs["context"]

    tokenizer.bos_token_id = 1
    prompt = tokenizer.apply_chat_template(input_text, tokenize=False, add_generation_prompt=True)
    print(prompt)

    text_inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = text_inputs["input_ids"].to("cuda")

    generation_config = GenerationConfig(
        temperature=inputs['temperature'],#0.1,
        do_sample=True,
        top_p=inputs['top_p'],#0.75,
        top_k=inputs['top_k'],#40,
        num_beams=inputs['num_beams'],#4,
        max_length=inputs['max_length'] #512,
    )
    start_time = time.time()
    with torch.no_grad():
        generation_output = model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=inputs['max_new_tokens'],
            early_stopping=True,
        )

    s = generation_output.sequences[0][input_ids.shape[-1]:]
    decoded_output = tokenizer.decode(s, skip_special_tokens=True).strip()
    end_time = time.time()
    elapsed_time = round(end_time-start_time, 4)
    print(decoded_output)
    print("Elapsed time: ", elapsed_time )
    # Write text output to a text file, which we'll retrieve when the async task completes
    output_path = "output.txt"
    with open(output_path, "w") as f:
        f.write(decoded_output)
    f.close()
    with open("ExecutionTime.txt", "w") as f:
        f.write(str(elapsed_time))
    f.close()

    # return {"llm_output":decoded_output}
