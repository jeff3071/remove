import pandas as pd
from PIL import Image
import streamlit as st
import streamlit_ext as ste
from streamlit_drawable_canvas import st_canvas
import numpy as np
import requests
import io

# Specify canvas parameters in application
# drawing_mode = st.sidebar.selectbox(
#     "Drawing tool:", ("freedraw", "point", "line", "rect", "circle", "transform")
# )

# stroke_width = st.sidebar.slider("Stroke width: ", 1, 50, 50)
# if drawing_mode == 'point':
#     point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
# stroke_color = st.sidebar.color_picker("Stroke color hex: ", "#e9ec12")
# bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
# bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg", "jpeg"])

# realtime_update = st.sidebar.checkbox("Update in realtime", True)

# image = None
# Download the fixed image
def convert_image(img: Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

def repaint_image(image: Image, mask: Image) -> Image: 
    files = {
        'image': ("flower.png", convert_image(image), 'image/png'),
        'mask': ("flower_mask.png", convert_image(mask), 'image/png'),
    }

    response = requests.post(
        "http://localhost:8000/uploadimage/",
        files=files,
    )

    response_json = response.json()
    img_array = np.array(response_json['image']).astype(np.uint8)
    return Image.fromarray(img_array).convert('RGB')

st.set_page_config(layout="wide", page_title="Image Background Remover")
bg_image = st.file_uploader("Background image:", type=["png", "jpg", "jpeg"])
st.markdown("\n")

if bg_image is not None:
    image_upload = Image.open(bg_image)
    image = np.array(image_upload)

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=35,
        stroke_color="#e9ec1290",
        # background_color=bg_color,
        background_image=Image.open(bg_image) if bg_image else None,
        update_streamlit=True,
        drawing_mode="freedraw",
        # point_display_radius=point_display_radius if drawing_mode == 'point' else 0,
        # key="canvas",
        height = image.shape[0],
        width = image.shape[1],
    )

    if canvas_result.image_data is not None and np.any(canvas_result.image_data):
        # st.image(canvas_result.image_data)
        
        # image_bytes = io.BytesIO()
        # image_upload.save(image_bytes, format="PNG")
        mask = Image.fromarray(canvas_result.image_data.astype(np.uint8)*255)

        result_img = repaint_image(image_upload, mask)

        ste.download_button(
            "Download fixed image", convert_image(result_img), "fixed.png", "image/png"
        )
        st.image(result_img)

    # if canvas_result.json_data is not None:
        # objects = pd.json_normalize(canvas_result.json_data["objects"])
        # for col in objects.select_dtypes(include=['object']).columns:
        #     objects[col] = objects[col].astype("str")
        # st.dataframe(objects)