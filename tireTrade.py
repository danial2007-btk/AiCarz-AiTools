import numpy as np
from io import BytesIO
from keras.utils import get_file
from keras.models import load_model
from keras.preprocessing import image

# Load your pre-trained model
# model = load_model('tyre.h5')

# URL of the Keras model in HDF5 format
H5_url = "https://aitoolmodel.s3.eu-west-2.amazonaws.com/models/tyre.h5"

# Load the Keras model
model = load_model(get_file("modelVGG.h5", H5_url))

def preprocess_image(contents):
    try:
        # Convert the image file to a numpy array
        img = image.load_img(BytesIO(contents), target_size=(224, 300))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        return img_array
    except Exception as e:
        raise ValueError(str(e))

def predict_image(img_array):
    # Make a prediction
    predictions = model.predict(img_array)
    predicted_class = 1 if predictions[0] > 0.5 else 0
    return "Good" if predicted_class == 1 else "Defected"
