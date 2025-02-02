#pip install cloudinary

# Video Upload to Cloudinary 
import cloudinary
import cloudinary.uploader

class CloudUploader:
    def __init__(self):
        # Step 1: Configure Cloudinary
        cloudinary.config(
            cloud_name="ddm6kadfn",  
            api_key="",  
            api_secret="" 
        )

    # Step 2: Function to Upload Video to Cloudinary
    def upload_to_cloudinary(self, local_video_path):
        print("Uploading video to Cloudinary...")
        try:
            response = cloudinary.uploader.upload(
                local_video_path,
                resource_type="video"
            )
            secure_url = response.get("secure_url")
            if secure_url:
                print(f"Uploaded URL: {secure_url}")
                return secure_url
            else:
                print("Error: Could not retrieve secure URL from Cloudinary response.")
                return None
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            return None
