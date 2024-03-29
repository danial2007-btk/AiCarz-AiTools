from carDetection import imageChecker
from NLPengine import descriptionChecker
from dataPipeline import getData

def carAdMain(carID):
    try:
        # check the car data
        carData = getData(carID)

        if carData == None:
            return {"Response": "The data of the requested Id is not available"}

        if carData[0].get('adStatus') != "Pending":
            return {"Response": "The Car AdStatus is not in Pending State"}

        ID = carData[0].get('Id')
        carImages = carData[0].get('images')
        carDesc = carData[0].get('description')

        if carImages is not None:
            imageRes = [imageChecker(image) for image in carImages]

            filtered_carImage = [img for img, result in zip(carImages, imageRes) if result == 1]

            # Find rejected images
            rejectedImages = list(set(carImages) - set(filtered_carImage))
            
            if len(filtered_carImage) == 0:
                return {'Id': ID, 'checkedDescription': carDesc, 'rejectedImages':rejectedImages,'adStatus': 'Rejected'}

            descriptionCheck = descriptionChecker(carDesc)

            return {'Id': ID, 'checkedDescription': descriptionCheck,'rejectedImages': rejectedImages, 'adStatus': 'Approved'}
        else:
            return {"Response": "No images available for this car ad."}

    except Exception as e:
        print (f"Error inside the carAdMain Function {e}")
    




