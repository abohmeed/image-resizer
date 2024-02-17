import io
import unittest
from PIL import Image
from app import app  # Import the Flask app

class TestImageResizingService(unittest.TestCase):
    def setUp(self):
        """Set up test client and other test variables."""
        self.app = app.test_client()
        self.app.testing = True

    def test_resize_endpoint_with_no_file(self):
        """Test resizing endpoint without file."""
        response = self.app.post('/resize', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('No file part in the request', response.data.decode('utf-8'))

    def test_resize_endpoint_with_no_filename(self):
        """Test resizing endpoint with no filename."""
        data = {
            'image': (io.BytesIO(), ''),  # Empty filename
        }
        response = self.app.post('/resize', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn('No selected file', response.data.decode('utf-8'))

    def test_resize_endpoint_with_valid_image_and_dimensions(self):
        """Test resizing endpoint with a valid image and dimensions."""
        # Create an example image
        img = Image.new('RGB', (800, 600), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        data = {
            'image': (img_bytes, 'test.jpg'),
            'width': '400'  # Only specify width to test dynamic height calculation
        }
        response = self.app.post('/resize', data=data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertIn('image/jpeg', response.content_type)

        # Load the image from the response and check its size
        resized_image = Image.open(io.BytesIO(response.data))
        self.assertEqual(resized_image.size, (400, 300))  # Expected size based on aspect ratio

if __name__ == '__main__':
    unittest.main()
