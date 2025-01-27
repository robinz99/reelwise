#!pip install selenium requests


import time
import os
import requests
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

def scrape_bing_images(query, num_images=10, headless=True):
    """
    Scrapes Bing Images using Selenium (Firefox) and returns a list of image URLs.

    :param query: The search query (str).
    :param num_images: Number of image links to collect (int).
    :param headless: Run Firefox in headless mode if True (bool).
    :return: List of image URLs (list).
    """

    # -- Construct the path to geckodriver.exe in the current directory --
    current_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(current_dir, "geckodriver.exe")

    # -- Set up Firefox options --
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("--headless")

    # -- Create a Service object pointing to geckodriver.exe --
    service = Service(driver_path)

    # -- Initialize the WebDriver (Firefox) --
    driver = webdriver.Firefox(service=service, options=firefox_options)

    try:
        # 1) Go to Bing Images search
        search_url = f"https://www.bing.com/images/search?q={query}&form=QBLH"
        driver.get(search_url)

        image_urls = set()
        last_height = driver.execute_script("return document.body.scrollHeight")

        # 2) Scroll and collect image URLs until we have enough
        while len(image_urls) < num_images:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Let images load

            # Find thumbnail <img> elements
            thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.mimg")

            for img in thumbnails:
                src = img.get_attribute("src")
                if src and "http" in src:
                    image_urls.add(src)
                if len(image_urls) >= num_images:
                    break

            # Check if we've reached the bottom (no more loading)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    finally:
        # 3) Quit the driver when done (important!)
        driver.quit()

    # Return only up to num_images
    return list(image_urls)[:num_images]


def download_images(image_urls, save_folder="images", prefix=""):
    """
    Downloads images from a list of URLs into a specified folder.

    :param image_urls: List of image URLs (list).
    :param save_folder: Directory to save the images (str).
    :param prefix: A string prefix to add to each filename (str).
    :return: List of file paths for the successfully downloaded images.
    """
    os.makedirs(save_folder, exist_ok=True)
    saved_paths = []

    for idx, url in enumerate(image_urls):
        # Incorporate prefix into file name so each is unique
        file_name = f"{prefix}image_{idx}.jpg"
        file_path = os.path.join(save_folder, file_name)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            saved_paths.append(file_path)
        except Exception as e:
            print(f"Failed to download {url} -> {e}")

    return saved_paths


def download_images_for_bing_prompts(image_prompts_output, save_folder="images"):
    """
    Parses the pipeline output from `generate_image_prompts`, retrieves each Bing prompt,
    and downloads exactly one image for each prompt into `save_folder`.
    """
    assistant_dict = image_prompts_output[0]["generated_text"][-1]
    json_string = assistant_dict["content"]
    prompts_list = json.loads(json_string)

    all_downloaded_paths = []

    # Loop over each prompt, with an index i
    for i, prompt in enumerate(prompts_list):
        # Scrape exactly 1 Bing image per prompt
        found_images = scrape_bing_images(query=prompt, num_images=1, headless=True)

        # Pass a unique prefix or index to avoid overwriting
        downloaded = download_images(found_images, save_folder=save_folder, prefix=f"prompt_{i}_")
        all_downloaded_paths.extend(downloaded)

    return all_downloaded_paths





from llamarizer import LLaMarizer  # Import from your llamarizer.py file

def main():
    # Example transcript
    lecture_transcript = (
        "Backward step-wise considers around P squared models instead of two to the P. "
        "It's a fantastic computational alternative to best-suffset selection, especially when P is moderate or large. "
        "But it's not guaranteed to give us the best model containing a particular subset of the P predictors. "
        "When we do best subset or forward or backward stepwise, we end up with these models M0 through MP. "
        "And I cannot just choose among them using R squared or using RSS because I'll always choose the biggest model. "
        "And again, that just boils down to the fact that these quantities are just based on the training error."
    )

    # 1) Instantiate LLaMarizer (CPU or GPU)
    llamarizer = LLaMarizer(use_cuda=False)

    # 2) Extract key concepts
    key_concepts_output = llamarizer.extract_key_concepts(lecture_transcript)
    print("\n--- Key Concepts Output ---")
    print(key_concepts_output)

    # 3) Generate script
    script_output = llamarizer.generate_script(lecture_transcript)
    print("\n--- Script Output ---")
    print(script_output)

    # 4) From the script output, extract the actual script text
    # script_output looks like:
    # [
    #   {
    #       "generated_text": [
    #           {"role": "system", "content": "..."},
    #           {"role": "user", "content": "..."},
    #           {"role": "assistant", "content": "{\"script\": \"...\"}"}
    #       ]
    #   }
    # ]
    assistant_dict = script_output[0]["generated_text"][-1]        # The last entry with role=assistant
    json_string = assistant_dict["content"]                        # A string like '{"script": "..."}'
    script_dict = json.loads(json_string)                          # Convert to Python dict
    script_text = script_dict["script"]                            # Extract the 'script' text

    # 5) Generate Bing prompts (one per sentence in the script)
    image_prompts_output = llamarizer.generate_image_prompts(script_text)
    print("\n--- Bing Image Prompts ---")
    print(image_prompts_output)


    #Static Bing prompts for testing, should be generated from the last step but llama always messes up json structure
    test_json_string = '["stepwise regression", "model selection", "data fitting"]'
    mock_image_prompts_output = [
    {
        "generated_text": [
            {
                "role": "assistant",
                "content": test_json_string
            }
        ]
    }
]
    
    bing_images_paths = download_images_for_bing_prompts(mock_image_prompts_output)
    print(bing_images_paths)


if __name__ == "__main__":
    main()