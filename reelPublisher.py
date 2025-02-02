# Publish to Instagram from Cloudinary 
import time
import requests

class ReelPublisher:
    def __init__(self, access_token, instagram_user_id, caption):
        self.ACCESS_TOKEN = access_token
        self.INSTAGRAM_USER_ID = instagram_user_id
        self.CAPTION = caption

    # Function to Upload Video to Instagram
    def upload_reel_to_instagram(self, video_url):
        print("Uploading video as a Reel to Instagram...")
        url = f"https://graph.facebook.com/v17.0/{self.INSTAGRAM_USER_ID}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": self.CAPTION,
            "access_token": self.ACCESS_TOKEN,
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

    # Function to Check Media Status
    def check_media_status(self, container_id):
        print("Checking media status...")
        url = f"https://graph.facebook.com/v17.0/{container_id}"
        payload = {
            "fields": "status",
            "access_token": self.ACCESS_TOKEN,
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

    # Function to Publish Reel
    def publish_reel(self, container_id):
        print("Publishing Reel to Instagram...")
        url = f"https://graph.facebook.com/v17.0/{self.INSTAGRAM_USER_ID}/media_publish"
        payload = {
            "creation_id": container_id,
            "access_token": self.ACCESS_TOKEN,
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

