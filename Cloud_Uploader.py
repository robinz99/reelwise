# Video Upload to Cloudinary 
import cloudinary
import cloudinary.uploader

# Step 1: Configure Cloudinary
cloudinary.config(
    cloud_name="ddm6kadfn",  
    api_key="",  
    api_secret="" 
)

# Step 2: Function to Upload Video to Cloudinary
def upload_to_cloudinary(local_video_path):
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

# Example Usage
if __name__ == "__main__":
    local_video_path = "/kaggle/input/og-jellyfish/OG_Jellyfish.mp4"  # Replace with our video path
    video_url = upload_to_cloudinary(local_video_path)

    if video_url:
        print(f"Cloudinary upload successful. Use this URL for Instagram: {video_url}")
        # Save the URL to a file or log for use in the next script
        with open("cloudinary_url.txt", "w") as file:
            file.write(video_url)
    else:
        print("Cloudinary upload failed.")