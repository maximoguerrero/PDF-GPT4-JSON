"""
gpt.py

This module provides the functionality to process a PDF file 
and extract data from the images using the GPT-4 Vision model.

It includes the following functions:
- process: The main function that orchestrates the extraction
           process. It takes a PDF file, extracts images from it, 
           and then uses the GPT-4 Vision model to extract 
           data from the images.
- extract_pages_as_images: A utility function that extracts 
                           images from a PDF file.
- clean_up_tmp_images_folder: A utility function that cleans up the 
                              temporary images folder after processing is done.

The module also imports several utility functions from the util module.
"""

import os
import sys
import json
from time import sleep
from pprint import pprint
from util import parse_json_string, process_image_to_json, resize_images, encode_images
from util import split_images, extract_pages_as_images, clean_up_tmp_images_folder
from util import get_image_files


def process(filename, folder, api_key, user_prompt: str = None,
            model: str = None, verbose: bool = False, cleanup: bool = False):
    """
    Process the PDF file and extract data from the images using GPT-4 Vision .

    Args:
        filename (str): The name of the PDF file.
        folder (str): The folder path where the PDF file is located.
        api_key (str): The API key for accessing the OpenAI GPT-4 Vision  API.
        user_prompt (str, optional): Custom prompt for GPT-4 Vision . Defaults to None.
        model (str, optional): The GPT-4 Vision  model to use. Defaults to None.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
        cleanup (bool, optional): Whether to clean up temporary files. Defaults to False.
    """
    # Change the current working directory to the specified directory
    os.chdir(folder)

    tmp_images_folder = './tmp_images'
    output_folder = './output'
    os.makedirs(tmp_images_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    image_encodings, image_files, filaname_image = do_images(
        filename, tmp_images_folder, verbose=False)

    # Set the OpenAI API key
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    # Define the prompt
    prompt = """
    You are an expert data analyst and you have been given a task to extract the data from the image.
    Extract the data you see as key value pairs in json? only output the json and nothing else.
    """

    # Use the user-provided prompt if available
    if user_prompt:
        prompt = user_prompt

    try:
        # Process each image using the GPT-4 Vision model
        for index, image_encoding in enumerate(image_encodings):

            if verbose:
                print(f"Processing image {
                    index + 1} of {len(image_encodings)}  {image_files[index]}...")

            # Check if JSON file for the image already exists in tmp folder
            json_file_path = os.path.join(
                output_folder, f"{image_files[index]}.json")
            if os.path.exists(json_file_path):
                if verbose:
                    print("JSON file already exists. Skipping...")
                continue

            had_errors = False
            json_file_data = None

            # Process the image using the GPT-4 Vision model
            response_dict = process_image_to_json(
                image_encoding, prompt, headers, model)

            # Check if the response contains an error
            if "error" in response_dict.keys():
                if verbose:
                    print("gpt returned error")
                had_errors = True
            else:
                # Parse the JSON string from the response
                json_file_data = parse_json_string(
                    response_dict["choices"][0]["message"]["content"])

                # Check if the JSON data is None
                if json_file_data is None:
                    if verbose:
                        print("parse_json_string retuned None")
                    had_errors = True

            # Check if the response contains an error or if the JSON data is None
            if had_errors:
                # write the response to a JSON file in the temporary folder for debugging
                json_file = os.path.join(
                    output_folder, f"{image_files[index]}.response.json")

                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(response_dict, f)

                continue

            # Write the response to a JSON file in the temporary folder
            json_file = os.path.join(
                output_folder, f"{image_files[index]}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(json_file_data, f)

            # limit the number of requests to 2 per second
            sleep(8)

        if cleanup:
            clean_up_tmp_images_folder(tmp_images_folder)
            os.removedirs(tmp_images_folder)

        new_output_folder = f"{filaname_image}_final_folders"
        os.rename(output_folder, new_output_folder)
        if verbose:
            print(f"Renaming output folder to {new_output_folder}")

        if verbose:
            print(f"JSON files saved in the folder '{new_output_folder}'")

    except Exception as e:
        print(f"An error occurred: {e}")
        # exit the program on error
        sys.exit()


def do_images(filename, tmp_images_folder, verbose=False):
    """
    Extracts images from a PDF file and performs various operations on them.

    Args:
        filename (str): The name of the PDF file.
        folder (str): The directory where the PDF file is located.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        list: A list of image encodings in base64 format.
    """

    # extract images from the PDF
    if verbose:
        print(f"Extracting images from the PDF '{filename}'...")

    filaname_image = ''.join(e for e in filename if e.isalnum())

    try:
        extract_pages_as_images(filename, tmp_images_folder, filaname_image)

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Failed to covert pages to image for gpt vision")
        # exit the program on error
        sys.exit()

    file_list = os.listdir(tmp_images_folder)
    if verbose:
        pprint(file_list)

    if len(file_list) == 0:
        print(f"No images found in the directory '{tmp_images_folder}'.")
        sys.exit()

    image_files = get_image_files(tmp_images_folder)

    # Resize images if they are too large
    resize_images(image_files, tmp_images_folder, verbose=verbose)

    # split images if they are too large
    split_images(image_files, tmp_images_folder, verbose=verbose)

    # update the list of images caused by splitting
    image_files = get_image_files(tmp_images_folder)

    # Encode the images to base64
    image_encodings = encode_images(
        image_files, tmp_images_folder, verbose=verbose)

    return image_encodings, image_files, filaname_image
