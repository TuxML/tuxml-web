from server import app

import os

from flask import request, render_template, redirect
from werkzeug.utils import secure_filename



ALLOWED_EXTENSIONS = {'config'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/prediction/', methods=["GET", "POST"])
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
                file.save(os.path.join(app.config["UPLOADS"], filename))
            return redirect(request.url)

    return render_template('prediction.html')