import json
import requests
import os
import re
from PIL import Image
import mimetypes
import base64
import pypdfium2 as pdfium
from split_image import split_image as si


def parse_json_string(json_string, verbose=False):
    def remove_comments(code):
        # Remove single-line comments
        code = re.sub(r'//.*', '', code)

        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

        return code

    try:
        json_string = remove_comments(json_string)
        # Remove the leading "```json " and trailing " ```" from the string
        if "```json" in json_string:
            start = json_string.index("```json") + len("```json")
            end = json_string.index("```", start)
            json_string = json_string[start:end]
        

        if verbose:
            print(json_string)

        # Parse the JSON string
        json_data = json.loads(json_string)

        return json_data
    except json.JSONDecodeError as e:
        # Handle JSON decoding errors
        print(f"Invalid JSON string ({e})")
        return None


def process_image_to_json(image_encoding, prompt, headers):
    # Define the data to send to the OpenAI API
    data = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": image_encoding
                    }
                ]
            }
        ],
        "max_tokens": 4096
    }

    # Send the request to the OpenAI API to process the image into JSON
    response = requests.post(
        'https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))
    response_dict = response.json()

    return response_dict


def extract_pages_as_images(pdf_file, tmp_images_folder, filaname_image="image"):
    # pdfuim used instead of convert_from_path because it canot handle super long pages

    pdf = pdfium.PdfDocument(pdf_file)
    n_pages = len(pdf)
    for page_number in range(n_pages):
        page = pdf.get_page(page_number)
        image_path = os.path.join(tmp_images_folder, f"{
                                  filaname_image}_{page_number+1}.jpg")
        bitmap = page.render(
            scale=1,
            rotation=0,
            crop=(0, 0, 0, 0)
        )
        pil_image = bitmap.to_pil()
        pil_image.save(image_path)


def resize_images(image_files, tmp_images_folder, verbose=False):
    # Resize images if they are too large
    for image_file in image_files:
        image_path = os.path.join(tmp_images_folder, image_file)
        with Image.open(image_path) as image:
            width, height = image.size
            if width > 1024:
                if verbose:
                    print(f"Resizing {image_file} from {width}x{
                        height} to 1024x{int(height * (1024 / width))}")
                resized_image = image.resize(
                    (1024, int(height * (1024 / width))))
                resized_image.save(image_path)


def split_images(image_files, tmp_images_folder, verbose=False):
    # Split images if they are too large
    for image_file in image_files:
        image_path = os.path.join(tmp_images_folder, image_file)
        if verbose:
            print(f"split to {image_path}")

        with Image.open(image_path) as image:
            width, height = image.size
            if height > 1024:
                num_splits = int(height / 1024)
                if verbose:
                    print(f"Splitting {image_file} into {num_splits} images")

                si(image_path, num_splits, 1, should_square=False,
                   output_dir=tmp_images_folder, should_cleanup=True)


def encode_images(image_files, tmp_images_folder, verbose=False):
    image_encodings = []
    for image_file in image_files:
        mime_type, _ = mimetypes.guess_type(image_file)
        with open(os.path.join(tmp_images_folder, image_file), "rb") as image:
            image_data = image.read()
            image_b64 = base64.b64encode(image_data).decode("utf-8")
            image_encoding = f"data:{mime_type};base64,{image_b64}"
            image_encodings.append(image_encoding)
            if verbose:
                print(image_file,  f"data:{mime_type};",
                    f"size: {len(image_data) / 1024:.2f} KB")
    return image_encodings


def get_image_files(directory):
    file_list = os.listdir(directory)
    # Define the list of image extensions allowed
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

    # Get a list of image files in the directory
    image_files = [file for file in file_list if any(
        file.endswith(ext) for ext in image_extensions)]

    # Filter out solid color images
    filtered_image_files = []
    for image_file in image_files:
        image_path = os.path.join(directory, image_file)
        if not is_solid_color(image_path):
            filtered_image_files.append(image_file)

    image_files = filtered_image_files
    image_files.sort()
    return image_files


def is_solid_color(image_path):
    with Image.open(image_path) as img:
        # Get the color of the first pixel
        first_pixel_color = img.getpixel((0, 0))

        # Check if all pixels have the same color as the first pixel
        for pixel in img.getdata():
            if pixel != first_pixel_color:
                return False

        return True


def clean_up_tmp_images_folder(tmp_images_folder):
    if not os.path.exists(tmp_images_folder):
        return

    image_files = os.listdir(tmp_images_folder)
    for image_file in image_files:
        image_path = os.path.join(tmp_images_folder, image_file)
        os.remove(image_path)
