import requests
from ultralytics import YOLO


# S3 model URL
model_url = 'https://aitoolmodel.s3.eu-west-2.amazonaws.com/models/bodyPannel.pt'

def model():
    
    # Download the model file
    response = requests.get(model_url)

    # Save the downloaded model file locally
    with open('model.pt', 'wb') as f:
        f.write(response.content)

    # Load the model
    model = YOLO('model.pt')

    return model