
import os

from flask import request, render_template, redirect
from werkzeug.utils import secure_filename



ALLOWED_EXTENSIONS = {'config'}
UPLOADS_DIRECTORY_PATH = "../uploads" 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def prediction():

    if request.method == "POST":
        
        if request.files:

            file = request.files["config"]

            if file.filename == "":
                print("File must have a filename")
                return redirect(request.url)

            if not allowed_file(file.filename):
                print("That file extension is not allowed")
                return redirect(request.url)

            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOADS_DIRECTORY_PATH, filename))
            return redirect(request.url)

    return render_template('prediction.html')