# Imagen Product & Human Recontextualizer

This Streamlit application provides a simple and effective user interface for Google's **Imagen Product Recontextualization API**. It is specifically designed to work reliably based on documented features, with a focus on human image editing and recontextualization.

The app allows you to take an image of a person or product and generate a new image placing them in a completely different scene, as described by your text prompt.


*(Image: Example of the app's interface)*


## Setup & Installation

Follow these steps to get the application running.

1.  **Create Project Files:**
    Create a new folder for your project and add the following two files inside it:

    *   `requirements.txt`
    *   `app.py`

2.  **Add File Content:**
    Copy the content from the sections below into their corresponding files.

3.  **Install Dependencies:**
    Open a terminal in your project folder and run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Authenticate with Google Cloud:**
    In the same terminal, authenticate your account with the `gcloud` CLI. This allows the script to securely access the API.
    ```bash
    gcloud auth application-default login
    ```
    A browser window will open for you to log in and approve permissions.

5.  **Run the App:**
    Start the Streamlit application:
    ```bash
    streamlit run app.py
    ```
    Your browser will open with the running application.

## How to Use

1.  **Configure GCP:** Enter your Google Cloud `Project ID` and `Region` in the sidebar.
2.  **Upload Image:** Upload the source image you want to edit.
3.  **Follow the Prompting Guide:**
    *   **Subject Description:** Describe the person or object you want to *keep* from the source image (e.g., "a man in a blue business suit").
    *   **Prompt:** Describe the *new scene* you want to place them in (e.g., "standing on a busy street in Tokyo at night").
4.  **Adjust Parameters:** Change the number of images, quality, etc., as needed.
5.  **Generate:** Click the "Generate Image" button and wait for the results.