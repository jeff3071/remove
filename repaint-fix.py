from PIL import Image
import streamlit as st
import streamlit_ext as ste
from streamlit_drawable_canvas import st_canvas
import numpy as np
import requests
import io

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


def image_resize(image, image_height, image_width):
    max_width = 720
    max_height = 720
    if image_width / image_height > max_width / max_height:
        new_image = image.resize((max_width, int(image_height * max_width / image_width)))
    else:
        new_image = image.resize((int(image_width * max_height / image_height), max_height))
    return new_image

st.set_page_config(layout="wide", page_title="Image Background Remover")
bg_image = st.file_uploader("Background image:", type=["png", "jpg", "jpeg"])
st.markdown("\n")
col1, col2 = st.columns(2)

if bg_image is not None:
    image_upload = Image.open(bg_image)
    image = np.array(image_upload)
    
    resize_image = image_resize(image_upload, image.shape[0], image.shape[1])
    new_image_size = np.array(resize_image)
    with col1:
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=35,
            stroke_color="#e9ec1290",
            background_image=resize_image,
            update_streamlit=True,
            drawing_mode="freedraw",
            height = new_image_size.shape[0],
            width = new_image_size.shape[1],
        )

    with col2:
        if canvas_result.image_data is not None and np.any(canvas_result.image_data):
            # st.image(resize_image)

            mask = Image.fromarray(canvas_result.image_data.astype(np.uint8)*255)

            result_img = repaint_image(image_upload, mask)

            ste.download_button(
                "Download fixed image", convert_image(result_img), "fixed.png", "image/png"
            )
            st.image(result_img)
