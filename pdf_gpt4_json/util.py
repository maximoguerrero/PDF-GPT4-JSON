"""
util.py

This module provides utility functions used throughout the application.

It includes the following functions:
- parse_json_string: Parses a JSON string and returns the corresponding Python object.
- remove_comments: Removes both single-line and multi-line comments from the given code.

The module also imports several libraries such as json, os, re, mimetypes, base64, 
requests, PIL, pypdfium2, and split_image.

"""

import json
import os
import re
import mimetypes
import base64
import requests
from PIL import Image
import pypdfium2 as pdfium
from split_image import split_image as si


def parse_json_string(json_string, verbose=False):
    """
    Parses a JSON string and returns the corresponding Python object.

    Args:
        json_string (str): The JSON string to parse.
        verbose (bool, optional): If True, prints the JSON string before parsing. Defaults to False.

    Returns:
        object: The Python object representing the parsed JSON.

    Raises:
        json.JSONDecodeError: If the JSON string is invalid and cannot be parsed.

    """

    def remove_comments(code):
        """
        Removes both single-line and multi-line comments from the given code.

        Args:
            code (str): The code from which comments should be removed.

        Returns:
            str: The code with comments removed.
        """
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
    except json.JSONDecodeError as error:
        # Handle JSON decoding errors
        print(f"Invalid JSON string ({error})")
        return None


def process_image_to_json(image_encoding, prompt, headers, model="gpt-4-vision-preview"):
    """
    Process an image into JSON using the OpenAI API.

    Args:
        image_encoding (str): The URL or base64-encoded image data.
        prompt (str): The prompt to provide to the model.
        headers (dict): The headers to include in the API request.
        model (str, optional): The model to use for processing the image. 
                               Defaults to "gpt-4-vision-preview".

    Returns:
        dict: The JSON response from the OpenAI API.

    Raises:
        Exception: If there is an error in the API request.

    """

    # Define the data to send to the OpenAI API
    data = {
        "model": model,
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
        'https://api.openai.com/v1/chat/completions', headers=headers,
        timeout=120, data=json.dumps(data))
    response_dict = response.json()

    return response_dict


def extract_pages_as_images(pdf_file, tmp_images_folder, filaname_image="image"):
    """
    Extracts pages from a PDF file and saves them as images in a temporary folder.

    Args:
        pdf_file (str): The path to the PDF file.
        tmp_images_folder (str): The path to the temporary folder where the images will be saved.
        filaname_image (str, optional): The base name for the image files. Defaults to "image".

    Returns:
        list: A list of filenames of the extracted images.

    """
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

    return os.listdir(tmp_images_folder)


def resize_images(image_files, tmp_images_folder, verbose=False):
    """
    Resize images if they are too large.

    Args:
        image_files (list): List of image file names.
        tmp_images_folder (str): Path to the temporary images folder.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    """
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
    """
    Split images if they are too large.

    Args:
        image_files (list): List of image file names.
        tmp_images_folder (str): Path to the temporary images folder.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    """

    for image_file in image_files:
        image_path = os.path.join(tmp_images_folder, image_file)
        if verbose:
            print(f"split to {image_path}")

        with Image.open(image_path) as image:
            _, height = image.size
            if height > 1024:
                num_splits = int(height / 1024)
                if verbose:
                    print(f"Splitting {image_file} into {num_splits} images")

                si(image_path, num_splits, 1, should_square=False,
                   output_dir=tmp_images_folder, should_cleanup=True, should_quiet=not verbose)


def encode_images(image_files, tmp_images_folder, verbose=False):
    """
    Encodes a list of image files into base64 strings.

    Args:
        image_files (list): A list of image file paths.
        tmp_images_folder (str): The path to the temporary folder where the images are stored.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        list: A list of base64-encoded image strings.

    """
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
    """
    Get a list of image files in the specified directory.

    Args:
        directory (str): The directory path to search for image files.

    Returns:
        list: A sorted list of image file names (including file extensions) in the directory.
    """
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
    """
    Check if an image is a solid color.

    Args:
        image_path (str): The path to the image file.

    Returns:
        bool: True if the image is a solid color, False otherwise.
    """
    with Image.open(image_path) as img:
        # Get the color of the first pixel
        first_pixel_color = img.getpixel((0, 0))

        # Check if all pixels have the same color as the first pixel
        for pixel in img.getdata():
            if pixel != first_pixel_color:
                return False

        return True


def clean_up_tmp_images_folder(tmp_images_folder):
    """
    Clean up the temporary images folder by removing all files inside it.

    Args:
        tmp_images_folder (str): The path to the temporary images folder.

    Returns:
        None
    """
    if not os.path.exists(tmp_images_folder):
        return

    image_files = os.listdir(tmp_images_folder)
    for image_file in image_files:
        image_path = os.path.join(tmp_images_folder, image_file)
        os.remove(image_path)
