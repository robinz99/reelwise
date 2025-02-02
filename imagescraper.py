#!pip install selenium requests


import time
import os
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

class ImageScraper:
    def __init__(self, save_folder="images"):
        """
        Initialize ImageScraper with a save folder for downloaded images.
        
        :param save_folder: Directory to save downloaded images (str)
        """
        self.save_folder = save_folder
        os.makedirs(save_folder, exist_ok=True)
        
        # Get path to geckodriver
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.driver_path = os.path.join(self.current_dir, "geckodriver.exe")

    def _setup_driver(self, headless=True):
        """
        Set up and return a Firefox webdriver instance.
        
        :param headless: Run Firefox in headless mode if True (bool)
        :return: Firefox WebDriver instance
        """
        firefox_options = Options()
        if headless:
            firefox_options.add_argument("--headless")
            
        service = Service(self.driver_path)
        return webdriver.Firefox(service=service, options=firefox_options)

    def scrape_bing_images(self, query, num_images=10, headless=True):
        """
        Scrapes Bing Images using Selenium (Firefox) and returns a list of image URLs.

        :param query: The search query (str)
        :param num_images: Number of image links to collect (int)
        :param headless: Run Firefox in headless mode if True (bool)
        :return: List of image URLs (list)
        """
        driver = self._setup_driver(headless)
        image_urls = set()

        try:
            # 1) Go to Bing Images search
            search_url = f"https://www.bing.com/images/search?q={query}&form=QBLH"
            driver.get(search_url)

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
            driver.quit()

        return list(image_urls)[:num_images]

    def download_images(self, image_urls, prefix=""):
        """
        Downloads images from a list of URLs into the specified save folder.

        :param image_urls: List of image URLs (list)
        :param prefix: A string prefix to add to each filename (str)
        :return: List of file paths for the successfully downloaded images
        """
        saved_paths = []

        for idx, url in enumerate(image_urls):
            # Incorporate prefix into file name so each is unique
            file_name = f"{prefix}image_{idx}.jpg"
            file_path = os.path.join(self.save_folder, file_name)

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
                saved_paths.append(file_path)
            except Exception as e:
                print(f"Failed to download {url} -> {e}")

        return saved_paths

    def download_images_for_bing_prompts(self, prompts_list):
        """
        Takes a list of Bing search prompts and downloads exactly one image for each prompt.
        
        :param prompts_list: List of strings containing Bing search prompts
        :return: List of paths to downloaded images
        """
        all_downloaded_paths = []

        for i, prompt in enumerate(prompts_list):
            # Scrape exactly 1 Bing image per prompt
            found_images = self.scrape_bing_images(query=prompt, num_images=1, headless=True)
            
            # Pass a unique prefix or index to avoid overwriting
            downloaded = self.download_images(found_images, prefix=f"prompt_{i}_")
            all_downloaded_paths.extend(downloaded)

        return all_downloaded_paths
