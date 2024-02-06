from bson import ObjectId
import time

from mongodb import carzcollection

collection = carzcollection

# the data Gather function below is for the Ad Status API
def getData(carID):
    carId = ObjectId(carID)

    query = {"_id": carId}

    data = []
    try:
        # Fetch the data
        result = list(carzcollection.find(query))

        for item in result:
            car_id = str(item.get("_id", ""))
            description = str(item.get("description", ""))
            carImages = (item.get("carImages", []))
            adStatus = str(item.get("adStatus",""))

            car_data = {
                "Id": car_id,
                "description": description,
                "images": carImages,
                "adStatus":adStatus
            }

            data.append(car_data)

        return data

    except Exception as e:
        return f"Error inside the getData {e}"