
import os
import numpy as np
import sys

from flask import request, render_template, redirect
from werkzeug.utils import secure_filename


from .ML.growML import get_x
from .ML.classifiers import useKNC, useDTC


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
                fparams_path =  DOWNLOADS_DIRECTORY_PATH  + "/" + "4.15" + "/params"

                if os.path.exists(fparams_path) and os.path.exists(file_path) :
                    

                    X = np.load( DOWNLOADS_DIRECTORY_PATH + "/" + "4.15" + "/X.npy")
                    y = np.load( DOWNLOADS_DIRECTORY_PATH + "/" + "4.15" + "/y.npy")

                    x = get_x(file_path,fparams_path)
                    os.remove(file_path)

                    print("X.shape :" , X.shape)
                    print("y.shape :" , y.shape)

                    print("x.shape :" , x.shape)

                    KNC_prediction = useKNC(X,y,x)
                    DTC_prediction = useDTC(X,y,x)


                    return render_template('prediction.html', KNC_prediction=KNC_prediction, DTC_prediction=DTC_prediction)

                else:
                	print("Missing :" + fparams_path + "  or  " + file_path )

    return render_template('prediction.html')