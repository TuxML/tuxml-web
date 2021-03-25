import numpy as numpy

from sklearn.neighbors import KNeighborsClassifier


def useKNC(X,y,x):
    
    print("y : " , y)
    
    print("X shape : " , X.shape)
    print("y shape : " , y.shape)
    print("x shape : " , x.shape)
    
    print("")
    
    #Use KNeighborsClassifier model
    model = KNeighborsClassifier()

    model.fit(X,y)

    model.score(X,y)

    
    prediction = model.predict(x)
    prediction = prediction[0]
    
    print("Predict_proba : " , model.predict_proba(x))
    print("Prediction : " , prediction)
    
    return prediction
    