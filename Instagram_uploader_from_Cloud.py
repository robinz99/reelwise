# Publish to Instagram from Cloudinary 
import time
import requests

# Step 1: Define Instagram Constants
ACCESS_TOKEN = ""  
INSTAGRAM_USER_ID = "17841472197943184"  
CAPTION = "Testing Jellyfish Video as Reel! With incorporating Cloudinary"

# Step 2: Function to Upload Video to Instagram
def upload_reel_to_instagram(video_url):
    print("Uploading video as a Reel to Instagram...")
    url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": CAPTION,
        "access_token": ACCESS_TOKEN,
    }
    response = requests.post(url, data=payload)
    print("Upload response:", response.json())
    if response.status_code == 200:
        container_id = response.json().get("id")
        print(f"Container ID: {container_id}")
        return container_id
    else:
        print("Error uploading video:", response.json())
        return None

# Step 3: Function to Check Media Status
def check_media_status(container_id):
    print("Checking media status...")
    url = f"https://graph.facebook.com/v17.0/{container_id}"
    payload = {
        "fields": "status",
        "access_token": ACCESS_TOKEN,
    }
    MAX_RETRIES = 20
    for _ in range(MAX_RETRIES):
        response = requests.get(url, params=payload)
        print("Status response:", response.json())
        if response.status_code == 200:
            status = response.json().get("status")
            print(f"Media status: {status}")
            if status == "READY" or "Finished" in status:  # Handle "Finished" status
                print("Media is ready for publishing.")
                return True
            elif status == "ERROR":
                print("Error processing media.")
                return False
        else:
            print("Error checking media status:", response.json())
            return False
        print("Media not ready. Waiting 10 seconds...")
        time.sleep(10)
    print("Media processing timed out.")
    return False

# Step 4: Function to Publish Reel
def publish_reel(container_id):
    print("Publishing Reel to Instagram...")
    url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_USER_ID}/media_publish"
    payload = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    }
    response = requests.post(url, data=payload)
    print("Publish response:", response.json())
    if response.status_code == 200:
        post_id = response.json().get("id")
        print(f"Reel published successfully. Post ID: {post_id}")
        return post_id
    else:
        print("Error publishing Reel:", response.json())
        return None

# Example Usage
if __name__ == "__main__":
    # Load the Cloudinary URL from the file
    try:
        with open("cloudinary_url.txt", "r") as file:
            video_url = file.read().strip()
    except FileNotFoundError:
        print("Error: Could not find 'cloudinary_url.txt'. Make sure the Cloudinary upload script has been run.")
        exit()

    # Step 1: Upload the video URL to Instagram
    container_id = upload_reel_to_instagram(video_url)

    if container_id and check_media_status(container_id):
        # Step 2: Publish the Reel
        publish_reel(container_id)
    else:
        print("Failed to upload or process Reel.")