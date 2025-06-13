import os,cv2
from flask import Flask, flash, request, render_template
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(filename, operation):
    print(f"Processing {filename} with operation: {operation}")
    
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    file_path = os.path.join('uploads', filename)

    img=cv2.imread(file_path)
    match operation:
        case 'cgray':
            ProcessedImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename=f"static/{filename}"
            cv2.imwrite(newFilename, ProcessedImg)
            return newFilename

        case 'cjpeg':
            newFilename=f'static/{filename.split(".")[0]}.jpeg'
            cv2.imwrite(newFilename, img)
            return newFilename
        
        case 'cwebp':
            newFilename=f'static/{filename.split(".")[0]}.webp'
            cv2.imwrite(newFilename, img)
            return newFilename

        case 'cpng':
            newFilename=f'static/{filename.split(".")[0]}.png'
            cv2.imwrite(newFilename, img)
            return newFilename
        
        case 'compress':
            new_filename = f'static/{name}_compressed{ext}'
            try:
                with Image.open(file_path) as im:
                    if ext in ['.jpg', '.jpeg']:
                        im.save(new_filename, format="JPEG", optimize=True, quality=30)
                    elif ext == '.png':
                        im.save(new_filename, format="PNG", optimize=True, compress_level=9)
                    elif ext == '.webp':
                        im.save(new_filename, format="WEBP", optimize=True, quality=30)
                    else:
                        return None  # Unsupported for compression
                return new_filename
            except Exception as e:
                print("Compression error:", e)
                return None
    pass

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method=='POST':
        operation = request.form.get('operation')
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return "File not selected"
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new=process_image(filename,operation)
            
            if new:
                download_link = f'/{new}'
                flash(f'''File successfully processed. 
                    <a href="{download_link}" target="_blank">Preview</a> or 
                    <a href="{download_link}" download>Download</a>''')

            else:
                flash('Failed to process the file. Check the file format or size.')
            return render_template("index.html")

    return render_template("index.html")

app.run(debug=True,port = 5000)