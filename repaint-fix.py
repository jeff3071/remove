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

st.set_page_config(layout="wide", page_title="Image Background Remover")
bg_image = st.file_uploader("Background image:", type=["png", "jpg", "jpeg"])
st.markdown("\n")
col1, col2 = st.columns(2)

if bg_image is not None:
    image_upload = Image.open(bg_image)
    image = np.array(image_upload)

    with col1:
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=35,
            stroke_color="#e9ec1290",
            background_image=image_upload,
            update_streamlit=True,
            drawing_mode="freedraw",
            height = image.shape[0],
            width = image.shape[1],
        )

    with col2:
        if canvas_result.image_data is not None and np.any(canvas_result.image_data):
            # st.image(image_upload)

            mask = Image.fromarray(canvas_result.image_data.astype(np.uint8)*255)

            result_img = repaint_image(image_upload, mask)

            ste.download_button(
                "Download fixed image", convert_image(result_img), "fixed.png", "image/png"
            )
            st.image(result_img)
