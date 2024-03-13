# test_util.py
import unittest
import json
import os
import numpy as np
import shutil
from PIL import Image
from pdf_gpt4_json.util import clean_up_tmp_images_folder, extract_pages_as_images, is_solid_color, parse_json_string, encode_images, get_image_files, resize_images, split_images


class TestUtilMethods(unittest.TestCase):

    # START TEST HELPER FUNCTIONS
    def get_test_folder(self, folder='imgs'):
        current_path = os.path.dirname(os.path.abspath(__file__))
        tmp_folder = os.path.join(current_path, folder)
        return tmp_folder

    def make_test_folder_copy(self, folder='imgs'):
        newfolder = self.get_test_folder(folder=folder) + '_copy'
        shutil.copytree(self.get_test_folder(folder=folder), newfolder,dirs_exist_ok=True)
        return newfolder

    def remove_test_folder_copy(self, folder='imgs'):
        shutil.rmtree(self.get_test_folder(folder=folder) +
                      '_copy', ignore_errors=True)

    # END TEST HELPER FUNCTIONS

    # START TEST CASES

    # JSON TESTS

    def test_parse_json_string(self):
        # Test case: valid JSON string with comments
        json_string = """
        // This is a comment
        {
            "key": "value" // Another comment
        }
        /* blah blah */
        """
        result = parse_json_string(json_string)
        expected = json.loads('{"key": "value"}')
        self.assertEqual(result, expected)

        # Test case: valid JSON string with comments
        json_string = """```json
        // This is a comment
        {
            "key": "value" // Another comment
        }
        ``` some other text
        """
        result = parse_json_string(json_string)
        expected = json.loads('{"key": "value"}')
        self.assertEqual(result, expected)

    # IMAGE PROCESSING TESTS

    def test_get_image_files(self):
        # Define the test directory
        directory = self.get_test_folder(folder='imgs')

        # Call the get_image_files function
        image_files = get_image_files(directory)

        # Check if the output is a list
        self.assertIsInstance(image_files, list)

        # Check if each item in the output list is a string
        for image_file in image_files:
            self.assertIsInstance(image_file, str)

        # Check if each file in the output list actually exists
        for image_file in image_files:
            self.assertTrue(os.path.exists(
                os.path.join(directory, image_file)))

    def test_encode_images(self):
        # Define the test image files and temporary images folder
        image_files = ['test_image.jpg']
        tmp_images_folder = self.get_test_folder(folder='imgs')

        # Call the encode_images function
        image_encodings = encode_images(image_files, tmp_images_folder)

        # Check if the output is a list
        self.assertIsInstance(image_encodings, list)

        # Check if the output list has the same length as the input list
        self.assertEqual(len(image_encodings), len(image_files))

        # Check if each item in the output list is a string (assuming the encoding is a string)
        for encoding in image_encodings:
            self.assertIsInstance(encoding, str)

    def test_is_solid_color(self):
        # Define the test image file
        current_path = self.get_test_folder(folder='imgs')
        image_file = os.path.join(current_path, 'test_image_solid.jpg')

        # Create a solid color image for testing
        img = Image.new('RGB', (10, 10), color=(73, 109, 137))
        img.save(image_file)

        # Call the is_solid_color function
        result = is_solid_color(image_file)

        # Check if the result is True
        self.assertTrue(result)

        # Now let's test with a non-solid color image
        img = Image.new('RGB', (10, 10), color=(73, 109, 137))
        img.putpixel((0, 0), (255, 255, 255))  # Change the color of one pixel
        img.save(image_file)

        # Call the is_solid_color function
        result = is_solid_color(image_file)

        # Check if the result is False
        self.assertFalse(result)

        # Clean up the test image file
        os.remove(image_file)

    def test_resize_images(self):
        # Define the test image files and temporary images folder
        image_files = ['test_image.jpg']
        tmp_images_folder = self.make_test_folder_copy(folder='imgs')

        image_files_sizes = []
        for image_file in image_files:
            image_path = os.path.join(tmp_images_folder, image_file)
            with Image.open(image_path) as img:
                image_files_sizes.append(img.size)

        # Call the resize_images function
        resize_images(image_files, tmp_images_folder)

        # Check if the output images exist and have the correct dimensions
        for idx, image_file in enumerate(image_files):
            old_image_file = image_files_sizes[idx]
            image_path = os.path.join(tmp_images_folder, image_file)
            with Image.open(image_path) as img:
                self.assertTrue(old_image_file != img.size)

        self.remove_test_folder_copy(folder='imgs')

    def test_split_images(self):
        
        tmp_images_folder = self.make_test_folder_copy(folder='imgs')

        # Define the input and expected output
        input_images = ['casablanca-2309610_1280.jpg']

        # Call the function with the test input
        split_images(input_images, tmp_images_folder)
        output_images = os.listdir(tmp_images_folder)
        output_images = [img for img in output_images if 'casablanca-2309610_1280_0' in img]
        
        self.remove_test_folder_copy(folder='imgs')


        self.assertEqual(len(output_images), 1)




    # PDF PROCESSING TESTS
    def test_extract_pages_as_images(self):
        # Define the test folder and temporary images folder
        folder = self.make_test_folder_copy(folder='pdf')
        if not os.path.exists(os.path.join(folder, 'tmp_images')):
            os.mkdir(os.path.join(folder, 'tmp_images'))

        tmp_images_folder = os.path.join(folder, 'tmp_images')

        # Change the current working directory to the test folder
        os.chdir(folder)
        # Define the input and expected output
        input_pdf = 'sample.pdf'
        fileimage = 'test_image'

        expected_output = ['test_image_1.jpg']

        # Call the function with the test input
        output_images = extract_pages_as_images(
            input_pdf, tmp_images_folder, filaname_image=fileimage)

        # Assert that the function output matches the expected output
        self.assertEqual(output_images, expected_output)

        # Clean up the temporary images folder
        shutil.rmtree(os.path.join(folder, 'tmp_images'), ignore_errors=True)
        os.chdir('..')
        self.remove_test_folder_copy(folder='pdf')


    # CLEANUP TESTS
    def test_clean_up_tmp_images_folder(self):
        
        tmp_images_folder = self.make_test_folder_copy(folder='imgs')

        # Call the cleanup function
        clean_up_tmp_images_folder(tmp_images_folder)

        # Assert that the dummy file no longer exists (i.e., the cleanup function worked)
        self.assertTrue(len(os.listdir(tmp_images_folder)) == 0)
        
        self.remove_test_folder_copy(folder='imgs')



    # END TEST CASES
if __name__ == '__main__':
    unittest.main()
