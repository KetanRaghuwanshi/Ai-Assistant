import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from io import BytesIO
from time import sleep
import platform  # To detect OS

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = "Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores

    # Generate the filenames for the images
    files = [f"{prompt}_{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)  # Correct path construction

        # Check if the file exists before attempting to open
        if os.path.exists(image_path):
            print(f"✅ Image found: {image_path}")

            try:
                # Open and verify the image before displaying
                with Image.open(image_path) as img:
                    img.verify()  # Checks if the image is valid
                    img.close()

                # Reopen and show the image
                if platform.system() == "Windows":
                    os.startfile(image_path)  # Opens in default viewer on Windows
                else:
                    img = Image.open(image_path)
                    img.show()

                sleep(1)  # Pause for 1 second before showing the next image
            except Exception as e:
                print(f"❌ Unable to open {image_path}: {e}")
        else:
            print(f"❌ Image does NOT exist: {image_path}")

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Retrieve API key
API_KEY = get_key('.env', 'HuggingFaceAPIKey')

# Ensure API key is valid
if not API_KEY:
    print("❌ API Key is missing! Check your .env file.")
else:
    print("🔑 API Key loaded successfully!")

headers = {"Authorization": f"Bearer {API_KEY}"}

# Async function to send a query to the Hugging Face API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}, {response.text}")
        return None  # Return None on failure

    return response.content

# Async function to generate images based on the given prompt
async def generate_images(prompt: str):
    tasks = []

    # Create 4 image generation tasks
    for i in range(1, 5):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Ensure the Data folder exists before saving images
    os.makedirs("Data", exist_ok=True)

    # Save the generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            try:
                image = Image.open(BytesIO(image_bytes))  # Convert raw bytes to image
                file_path = os.path.join("Data", f"{prompt.replace(' ', '_')}_{i + 1}.jpg")
                image = image.convert("RGB")  # Ensure it's in RGB mode
                image.save(file_path, format="JPEG")  # Save properly
                print(f"✅ Image saved: {file_path}")
            except Exception as e:
                print(f"❌ Error processing image {i + 1}: {e}")
                print(f"📝 API Response: {image_bytes[:500]}")  # Debugging: Print first 500 bytes of response

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_images(prompt))
    open_images(prompt)

# Main loop to monitor for image generation requests
print("🔄 Monitoring ImageGeneration.data for new image requests...")

while True:
    try:
        # Read the status and prompt from the data file
        with open("Frontend/Files/ImageGeneration.data", "r") as f:
            Data = f.read().strip()

        if not Data:
            sleep(1)
            continue

        Prompt, Status = Data.split(",")
        Prompt, Status = Prompt.strip(), Status.strip()

        print(f"📌 Parsed Prompt: {Prompt}, Status: {Status}")

                # If the status indicates an image generation request
        if Status.strip().lower() == "true":
            print("🚀 Generating Images...")
            GenerateImages(prompt=Prompt.strip())

            # Reset the status in the file after generating images
            with open("Frontend/Files/ImageGeneration.data", "w") as f:
                f.write("False,False")

            print("✅ Image generation complete. Exiting program.")
            os._exit(0)  # Forces the script to terminate completely

        else:
            sleep(1)  # Wait before checking again


    except Exception as e:
        print(f"⚠️ Error: {e}")
        sleep(1)



