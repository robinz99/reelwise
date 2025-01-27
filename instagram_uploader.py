import time
import requests

# Step 1: Define Constants
ACCESS_TOKEN = ""  # Replace with your token
INSTAGRAM_USER_ID = "17841472197943184"   # Replace with your Instagram User ID
VIDEO_URL = "https://test-videos.co.uk/vids/jellyfish/mp4/h264/1080/Jellyfish_1080_10s_1MB.mp4"  # Test video URL
CAPTION = "Testing Jellyfish Video as Reel!"

# Step 2: Upload Video as a Reel
def upload_reel():
    print("Uploading video as a Reel to Instagram...")
    url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": VIDEO_URL,
        "caption": CAPTION,
        "access_token": ACCESS_TOKEN,
    }
     response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Video uploaded successfully.")
        container_id = response.json().get("id")
        print(f"Container ID: {container_id}")
        return container_id
    else:
        print("Error uploading video:", response.json())
        return None
# Step 3: Poll Media Status
def check_media_status(container_id):
    print("Checking media status...")
    url = f"https://graph.facebook.com/v17.0/{container_id}"
    payload = {
        "fields": "status_code",
        "access_token": ACCESS_TOKEN,
    }
    while True:
        response = requests.get(url, params=payload)
        if response.status_code == 200:
            status = response.json().get("status_code")
            print(f"Media status: {status}")
            if status == "FINISHED":
                print("Media is ready for publishing.")
                return True
            elif status == "ERROR":
                print("Error processing media.")
                return False
        else:
            print("Error checking media status:", response.json())
            return False
        print("Media not ready. Waiting 5 seconds...")
        time.sleep(5)  # Wait before checking again
        # Step 4: Publish the Reel
def publish_reel(container_id):
    print("Publishing Reel to Instagram...")
    url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_USER_ID}/media_publish"
    payload = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Reel published successfully.")
        post_id = response.json().get("id")
        print(f"Post ID: {post_id}")
        return post_id
    else:
        print("Error publishing Reel:", response.json())
        return None
    # Main Workflow
if __name__ == "__main__":
    container_id = upload_reel()
    if container_id and check_media_status(container_id):
        publish_reel(container_id)
    else:
        print("Failed to upload or process Reel.")