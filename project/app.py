from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from secure_delete_tool import secure_delete_file, secure_delete_directory, cryptographic_erase, wipe_free_space

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Use .get() to avoid BadRequestKeyError if the key is missing
        operation = request.form.get('operation')
        passes = int(request.form.get('passes', 3))

        # Check if the 'file' key exists in request.files
        if 'file' not in request.files:
            flash('No file part in the request', 'danger')
            return redirect(request.url)

        uploaded_files = request.files.getlist('file')
        if not uploaded_files or uploaded_files[0].filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        for file in uploaded_files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            if operation == 'delete':
                if os.path.isdir(file_path):
                    secure_delete_directory(file_path, passes)
                else:
                    secure_delete_file(file_path, passes)
                flash(f"'{filename}' securely deleted.", 'success')

            elif operation == 'cryptographic_erase':
                if os.path.isdir(file_path):
                    flash(f"Cryptographic erase is not supported for directories.", 'danger')
                else:
                    cryptographic_erase(file_path)
                flash(f"'{filename}' cryptographically erased.", 'success')

            elif operation == 'wipe_free_space':
                if os.path.exists(file_path):
                    wipe_free_space(file_path, passes)
                    flash(f"Free space on '{file_path}' wiped.", 'success')
                else:
                    flash(f"Drive path '{file_path}' does not exist.", 'danger')

            # Clean up the uploaded file after processing
            if os.path.exists(file_path):
                os.remove(file_path)

        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

