import pandas as pd
from PIL import Image, ImageChops
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import torch
import json
import requests
import io

# Specify canvas parameters in application
drawing_mode = st.sidebar.selectbox(
    "Drawing tool:", ("freedraw", "point", "line", "rect", "circle", "transform")
)

stroke_width = st.sidebar.slider("Stroke width: ", 1, 50, 50)
if drawing_mode == 'point':
    point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ", "#e9ec12")
bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg", "jpeg"])

realtime_update = st.sidebar.checkbox("Update in realtime", True)

image = None
if bg_image is not None:
    # print(stroke_color)
    stroke_color += "90"
    image_upload = Image.open(bg_image)
    image = np.array(image_upload)
    # print(image.shape)

    # Create a canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=Image.open(bg_image) if bg_image else None,
        update_streamlit=realtime_update,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == 'point' else 0,
        key="canvas",
        height = image.shape[0] if image is not None else 400,
        width = image.shape[1] if image is not None else 600,
    )

    if image is not None:
        canvas_result.height = image.shape[0]
        canvas_result.width = image.shape[1]
        # print(canvas_result)

    # Do something interesting with the image data and paths
    if canvas_result.image_data is not None and np.any(canvas_result.image_data):
        st.image(canvas_result.image_data)
        
        image_bytes = io.BytesIO()
        image_upload.save(image_bytes, format="PNG")
        mask = Image.fromarray(canvas_result.image_data.astype(np.uint8)*255)
        mask_bytes = io.BytesIO()
        mask.save(mask_bytes, format="PNG")
        files = {
            'image': ("flower.png", image_bytes.getvalue(), 'image/png'),
            'mask': ("flower_mask.png", mask_bytes.getvalue(), 'image/png'),
        }

        response = requests.post(
            "http://localhost:8000/uploadimage/",
            files=files,
        )

        response_json = response.json()
        img_array = np.array(response_json['image']).astype(np.uint8)

        # Image.fromarray(img_array).convert('RGB').show()
        st.image(Image.fromarray(img_array).convert('RGB'))
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"]) # need to convert obj to str because PyArrow
        for col in objects.select_dtypes(include=['object']).columns:
            objects[col] = objects[col].astype("str")
        st.dataframe(objects)