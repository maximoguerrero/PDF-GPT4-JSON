# test_util.py
import unittest
import json, os
import numpy as np
import shutil
from PIL import Image
from pdf_gpt4_json.util import is_solid_color, parse_json_string ,encode_images, get_image_files, resize_images

class TestUtilMethods(unittest.TestCase):
    
    def get_test_image_folder(self):
            current_path = os.path.dirname(os.path.abspath(__file__))
            tmp_images_folder = os.path.join(current_path, 'imgs')
            return tmp_images_folder

    def make_test_image_folder_copy(self):
        newfolder = self.get_test_image_folder() + '_copy'
        shutil.copytree(self.get_test_image_folder(), newfolder)
        return newfolder
    
    def remove_test_image_folder_copy(self):
        shutil.rmtree(self.get_test_image_folder() + '_copy', ignore_errors=True)

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


    def test_get_image_files(self):
        # Define the test directory
        directory = self.get_test_image_folder()
        
        # Call the get_image_files function
        image_files = get_image_files(directory)
        
        # Check if the output is a list
        self.assertIsInstance(image_files, list)
        
        # Check if each item in the output list is a string
        for image_file in image_files:
            self.assertIsInstance(image_file, str)
            
        # Check if each file in the output list actually exists
        for image_file in image_files:
            self.assertTrue(os.path.exists(os.path.join(directory, image_file)))

    def test_encode_images(self):
        # Define the test image files and temporary images folder
        image_files = ['test_image.jpg']
        tmp_images_folder = self.get_test_image_folder()
        
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
        current_path = self.get_test_image_folder()
        image_file = os.path.join(current_path, 'test_image_solid.jpg')

        
        # Create a solid color image for testing
        img = Image.new('RGB', (10, 10), color = (73, 109, 137))
        img.save(image_file)
        
        # Call the is_solid_color function
        result = is_solid_color(image_file)
        
        # Check if the result is True
        self.assertTrue(result)

        # Now let's test with a non-solid color image
        img = Image.new('RGB', (10, 10), color = (73, 109, 137))
        img.putpixel((0,0), (255,255,255))  # Change the color of one pixel
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
        tmp_images_folder = self.make_test_image_folder_copy()
        
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

        self.remove_test_image_folder_copy()

if __name__ == '__main__':
    unittest.main()
