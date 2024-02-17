from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

@app.route('/resize', methods=['POST'])
def resize_image():
    if 'image' not in request.files:
        return 'No file part in the request', 400
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400

    # Assume width is provided, or height, but not necessarily both
    width = request.form.get('width')
    height = request.form.get('height')

    try:
        image = Image.open(file.stream)
        orig_width, orig_height = image.size
        
        # Calculate the missing dimension
        if width:
            width = int(width)
            ratio = width / orig_width
            height = round(orig_height * ratio)
        elif height:
            height = int(height)
            ratio = height / orig_height
            width = round(orig_width * ratio)
        else:
            return 'Width or height required', 400

        resized_image = image.resize((width, height), Image.LANCZOS)
        img_byte_arr = io.BytesIO()
        resized_image.save(img_byte_arr, format=image.format)
        img_byte_arr.seek(0)  # Move to the beginning of the BytesIO buffer

        # Send the direct binary data
        return send_file(img_byte_arr, mimetype='image/jpeg')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(port=5555, debug=True)
