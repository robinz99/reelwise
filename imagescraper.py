import time
import os
import requests

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


def download_images(image_urls, save_folder="images"):
    """
    Downloads images from a list of URLs into a specified folder.

    :param image_urls: List of image URLs (list).
    :param save_folder: Directory to save the images (str).
    :return: List of file paths for the successfully downloaded images.
    """
    os.makedirs(save_folder, exist_ok=True)
    saved_paths = []

    for idx, url in enumerate(image_urls):
        # Use a simple naming scheme with .jpg extension
        file_name = f"image_{idx}.jpg"
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


if __name__ == "__main__":
    # Example usage:
    query_prompt = "futuristic office background"

    # 1) Scrape Bing for image URLs
    results = scrape_bing_images(query_prompt, num_images=5, headless=True)
    print("Image URLs found:", results)

    # 2) Download the images
    downloaded_files = download_images(results, save_folder="firefox_images")
    print("Downloaded files:", downloaded_files)
