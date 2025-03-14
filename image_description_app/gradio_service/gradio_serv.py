import gradio as gr
import os
from .handlers import image_handler
from .handlers import history_handler
from dotenv import load_dotenv
load_dotenv()

API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL')

model_choices = ["Salesforce/blip-image-captioning-base", "Salesforce/blip-image-captioning-large"]

image_input = gr.Image(label="Загрузите изображение")
model_dropdown = gr.Dropdown(choices=model_choices, value=model_choices[0], label="Выберите модель для описания")
description_output = gr.Textbox(label="Описание")

history_output = gr.Gallery(label="История запросов", columns=5, rows=2) # rows * columns = 10 initial load
load_more_button = gr.Button("Загрузить больше")
offset_state = gr.State(0)  # для хранения текущего offset

interface = gr.Interface(
    fn=lambda image, model_name: image_handler.describe_image(API_GATEWAY_URL, image, model_name),
    inputs=[image_input, model_dropdown],
    outputs=description_output,
    title="Сервис описания изображений",
    description="Загрузите изображение, выберите модель.",
)

interface.load(
    lambda: history_handler.load_history(API_GATEWAY_URL),
    [],
    [history_output]
)

load_more_button.click(
    lambda offset, gallery: history_handler.load_more(API_GATEWAY_URL, offset, gallery),
    inputs=[offset_state, history_output],
    outputs=[offset_state, history_output]
)

interface.launch(server_name="0.0.0.0", server_port=7860)