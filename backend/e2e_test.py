from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import unittest
from PIL import Image
import io
import os


def create_dummy_image():
    # Create an image with RGB mode and size 100x100 with a red color
    img = Image.new("RGB", (1000, 1000), color=(255, 0, 0))

    # Save the image to a bytes buffer
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")

    # Move to the beginning of the BytesIO buffer
    img_byte_arr.seek(0)

    return img_byte_arr


class ImageResizerE2ETest(unittest.TestCase):
    def setup_method(self, method):
        # Setup Chrome webdriver
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8080")  # Replace with your app's URL

    def teardown_method(self, method):
        self.driver.quit()

    def test_image_resize(self):
        # Locate the file upload element
        upload_selector = "input[id=imageFile]"
        upload_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, upload_selector))
        )
        dummy_image_bytes = create_dummy_image()
        temp_image_path = os.path.join(os.getcwd(), "dummy_image.jpg")
        with open(temp_image_path, "wb") as f:
            f.write(dummy_image_bytes.getvalue())
        upload_element.send_keys(temp_image_path)
        # Input width
        width_input = self.driver.find_element(By.ID, "width")
        # Example resize dimensions
        width_input.send_keys("800")
        form_selector = "form[id='uploadForm']"
        # Wait for the form to be visible and interactable
        form_element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, form_selector))
        )
        # Submit the form
        form_element.submit()

        # Wait for the image to be processed and check for the result
        image = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "resultImage"))
        )
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return arguments[0].complete", image)
        )
        try:
            # Wait for the image to be present and have non-zero dimensions
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.find_element(By.ID, "resultImage")
                and driver.execute_script(
                    "return arguments[0].naturalWidth > 0 && arguments[0].naturalHeight > 0;",
                    driver.find_element(By.ID, "resultImage"),
                )
            )

            # Once the wait is complete, fetch the image again to ensure we have the loaded element
            image = self.driver.find_element(By.ID, "resultImage")

            # Then retrieve its dimensions
            width = self.driver.execute_script(
                "return arguments[0].naturalWidth", image
            )
            height = self.driver.execute_script(
                "return arguments[0].naturalHeight", image
            )

            # Expected dimensions
            expected_width = 800  # Example expected width
            expected_height = 800  # Example expected height

            # Assert dimensions are as expected
            self.assertEqual(
                width,
                expected_width,
                f"Image width is expected to be {expected_width}, but got {width}",
            )
            self.assertEqual(
                height,
                expected_height,
                f"Image height is expected to be {expected_height}, but got {height}",
            )
        except TimeoutException:
            self.fail("Timed out waiting for image to load its natural dimensions")


if __name__ == "__main__":


    
    test = ImageResizerE2ETest()
    test.setup_method(None)
    try:
        test.test_image_resize()
    finally:
        test.teardown_method(None)
