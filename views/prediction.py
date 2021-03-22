
import os
import numpy as np

from flask import request, render_template, redirect
from werkzeug.utils import secure_filename
from ..ML.growML import get_x, useKNC 



ALLOWED_EXTENSIONS = {'config'}
UPLOADS_DIRECTORY_PATH = "../uploads" 
DOWNLOADS_DIRECTORY_PATH = "../downloads"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def prediction_view():

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
                file_path = UPLOADS_DIRECTORY_PATH + "/" + filename
                fparams_path =  DOWNLOADS_DIRECTORY_PATH  + "/" + '4.15' + "/" + params 
                x = get_x(file_path,fparams_path)

                X = np.load( DOWNLOADS_DIRECTORY_PATH + "/" + '5.4' + "/X.npy")
                y = np.load( DOWNLOADS_DIRECTORY_PATH + "/" + '5.4' + "/y.npy")

                prediction = useKNC(X,y,x)

                print(prediction)

            return redirect(request.url)

    return render_template('prediction.html')