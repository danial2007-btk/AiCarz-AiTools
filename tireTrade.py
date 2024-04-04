import numpy as np
from io import BytesIO
from keras.utils import get_file
from keras.models import load_model
from PIL import Image


# URL of the Keras model in HDF5 format
H5_url = "https://aitoolmodel.s3.eu-west-2.amazonaws.com/models/tyre_checker.h5"

# Load the Keras model
model = load_model(get_file("tyre_checker.h5", H5_url), compile=False)

# model = load_model("tyre_checker.h5", compile=False)


def preprocess_image(contents):
    try:
        img = Image.open(BytesIO(contents)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array.astype('float32') / 255.0
        return img_array
    except Exception as e:
        raise ValueError(str(e))

def predict_image(img_array):
    # Make a prediction
    predictions = model.predict(img_array)
    print(predictions)
    predicted_class = np.argmax(predictions)
    if predicted_class == 0:
        return "Defected"
    elif predicted_class == 1:
        return "Good"
    elif predicted_class == 2:
        return "Not Tyre"

