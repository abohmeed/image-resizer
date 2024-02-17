from flask import Flask, request, send_file, jsonify
from PIL import Image
import io

app = Flask(__name__)

@app.route('/resize', methods=['POST'])
def resize_image():
    # Ensure there's a file in the request
    if 'file' not in request.files:
        response = jsonify({"error": "No file part in the request"})
        response.status_code = 400
        response.headers['Content-Type'] = 'application/json'
        return response

    file = request.files['file']
    if file.filename == '':
        response = jsonify({"error": "No selected file"})
        response.status_code = 400
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Ensure the 'size' parameter exists and is valid
    size_param = request.args.get('size')
    if not size_param:
        response = jsonify({"error": "Size parameter is missing. Provide as '?size=100'."})
        response.status_code = 400
        response.headers['Content-Type'] = 'application/json'
        return response

    try:
        max_size = int(size_param)
    except ValueError:
        response = jsonify({"error": f"Invalid size parameter: {size_param}. Must be an integer."})
        response.status_code = 400
        response.headers['Content-Type'] = 'application/json'
        return response

    try:
        # Process the image
        image = Image.open(file.stream)
        aspect_ratio = image.width / image.height
        if image.width >= image.height:
            new_width = min(image.width, max_size)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = min(image.height, max_size)
            new_width = int(new_height * aspect_ratio)

        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        output_format = 'JPEG' if image.format not in ['JPEG', 'PNG'] else image.format

        buf = io.BytesIO()
        resized_image.save(buf, format=output_format)
        buf.seek(0)

        response = send_file(buf, mimetype=f'image/{output_format.lower()}')
        return response
    except Exception as e:
        response = jsonify({"error": f"Error processing the image: {str(e)}"})
        response.status_code = 500
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.run(debug=True, port=5555)
