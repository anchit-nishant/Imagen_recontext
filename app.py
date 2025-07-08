import streamlit as st
import base64
import requests
import json
import google.auth
import google.auth.transport.requests

# --- App Configuration ---
st.set_page_config(
    page_title="Imagen Recontextualizer",
    page_icon="🎭",
    layout="wide"
)

# --- Helper Functions ---
def encode_image(uploaded_file):
    """Encodes the uploaded image file to base64."""
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    return None

def get_gcp_token():
    """Gets the default GCP access token."""
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

# --- Main App UI ---
st.title("🎭 Imagen Recontextualizer")
st.markdown("A simplified and reliable UI for Google's Imagen API, focused on human and product image editing.")

# --- Sidebar for GCP Configuration ---
with st.sidebar:
    st.header("☁️ GCP Configuration")
    st.markdown("Enter your Google Cloud project details here.")
    project_id = st.text_input("Google Cloud Project ID", help="Your GCP project ID.")
    region = st.selectbox("Region", ["us-central1"], help="The model is available in this region.")

# --- Main Content Area ---
st.header("1. The Prompting Guide (How to Use)")
st.info(
    """
    This API works by separating the **Subject** (what to keep) from the **Scene** (what to generate).
    
    - **Subject Description:** Describe the person or object you want to extract from your uploaded image. This tells the AI *what to keep*.
      - *Example:* `a man in a blue business suit`
      - *Example:* `a pair of high-top red sneakers`

    - **Prompt:** Describe the new background and scene where you want to place your subject. This tells the AI *what to create*.
      - *Example:* `standing on a busy street in Tokyo at night, with neon signs`
      - *Example:* `on a display stand in a luxury shoe store`
    """,
    icon="💡"
)

st.header("2. Provide Your Inputs")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Source Image(s)")
    uploaded_product_images = st.file_uploader(
        "Upload 1 to 3 images of your subject (person or product).",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True
    )
    
    # --- The st.warning note has been removed from here ---

    if uploaded_product_images:
        if len(uploaded_product_images) > 3:
            st.error("Please upload a maximum of 3 images.")
            uploaded_product_images = uploaded_product_images[:3]
        
        cols = st.columns(len(uploaded_product_images))
        for i, uploaded_image in enumerate(uploaded_product_images):
            with cols[i]:
                st.image(uploaded_image, caption=f"Source {i+1}", use_container_width=True)

with col2:
    st.subheader("Descriptions")
    subject_description = st.text_input(
        "**Subject Description (What to keep):**",
        placeholder="e.g., a man in a blue business suit",
        help="Describe the person/object in your source image that you want to place in a new scene."
    )
    prompt = st.text_area(
        "**Prompt (The new scene):**",
        height=150,
        placeholder="e.g., standing on a busy street in Tokyo at night",
        help="Describe the new background or scene you want to generate."
    )

st.header("3. Configure Generation Parameters")
with st.expander("⚙️ Generation Parameters", expanded=True):
    param_col1, param_col2 = st.columns(2)
    with param_col1:
        sample_count = st.slider("Number of Images", 1, 4, 1, help="How many image variations to generate.")
        base_steps = st.slider(
            "Generation Quality / Speed", 10, 100, 32,
            help="Higher values can improve quality but are slower. Lower values are faster. The default (32) is a good balance."
        )
    with param_col2:
        enhance_prompt = st.toggle(
            "Enhance Prompt", True,
            help="Allows Google's AI to rewrite your prompt for potentially more creative results. Turn off for a more literal interpretation."
        )
        person_generation = st.selectbox("Allow People", ["allow_adult", "dont_allow", "allow_all"], index=0, help="Controls the generation of people in the image.")
        seed_input = st.text_input("Seed (Optional)", placeholder="e.g., 12345", help="Use the same number to get reproducible results. Leave empty for random.")
        seed = int(seed_input) if seed_input.isdigit() else None

st.divider()

if st.button("Generate Image ✨", type="primary", use_container_width=True):
    if not all([project_id, region, uploaded_product_images, subject_description, prompt]):
        st.error("❌ Please fill in all fields: Project ID, Region, Subject Description, Prompt, and upload at least one image.")
    elif len(uploaded_product_images) > 3:
        st.error("Please upload a maximum of 3 images.")
    else:
        with st.spinner("Recontextualizing your image... This can take a moment."):
            try:
                # --- API Call Logic ---
                access_token = get_gcp_token()
                endpoint_url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/imagen-product-recontext-preview-06-30:predict"
                
                product_images_payload = []
                for uploaded_file in uploaded_product_images:
                    encoded_string = encode_image(uploaded_file)
                    product_images_payload.append({"image": {"bytesBase64Encoded": encoded_string}})

                instance_data = {
                    "prompt": prompt,
                    "productImages": product_images_payload,
                    "productDescription": subject_description
                }
                
                parameters_data = {
                    "sampleCount": sample_count,
                    "baseSteps": base_steps,
                    "enhancePrompt": enhance_prompt,
                    "personGeneration": person_generation,
                }
                if seed is not None:
                    parameters_data["seed"] = seed

                payload = {"instances": [instance_data], "parameters": parameters_data}
                headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
                
                response = requests.post(endpoint_url, headers=headers, data=json.dumps(payload))
                response.raise_for_status()
                response_data = response.json()

                # --- Display Results ---
                st.success("✅ Generation complete!")
                st.header("4. Generated Results")
                
                if 'predictions' in response_data and response_data['predictions']:
                    predictions = response_data['predictions']
                    cols = st.columns(len(predictions))
                    for i, prediction in enumerate(predictions):
                        with cols[i]:
                            b64_image = prediction.get("bytesBase64Encoded")
                            if b64_image:
                                img_bytes = base64.b64decode(b64_image)
                                st.image(img_bytes, caption=f"Result {i+1}", use_container_width=True)
                else:
                    st.error("API returned a success status but no predictions were found. This can happen with very restrictive prompts.")
                    st.json(response_data)

            except requests.exceptions.HTTPError as err:
                st.error(f"HTTP Error: {err.response.status_code} {err.response.reason}")
                st.error(f"Response Content: {err.response.text}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")