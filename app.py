from fastapi import FastAPI, HTTPException, Depends, Query, status, UploadFile, File
from contextlib import asynccontextmanager
from pydantic import BaseModel
from bson import ObjectId
import uvicorn
import time

from main import carAdMain
from mongodb import carzcollection, mongodbConn

try:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load the ML model
        print("======> loading statup event")
        # ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
        yield
        # Clean up the ML models and release the resources
        print("xxxxxxxx   shurting down event")
        mongodbConn.close()
        print("mongodb disconnected")

    app = FastAPI(lifespan=lifespan)

    # The valid API key
    API_key = "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"

    # Dependency to check API key
    def check_api_key(api_key: str = Query(..., description="API Key")):
        if api_key != API_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return api_key

    # **************************       APP CHECKING         **************************

    # Root Endpoint
    @app.get("/")
    def read_root():
        return {"message": "App is running successfully"}

    # **************************       Car AD Checker API ENDPOINT         **************************

    class AdCarIdInput(BaseModel):
        carid: str  # Car ID as input

    # car AdChecking API Endpoint
    # @profile
    @app.post("/adChecker")
    async def car_ad_checker(
        car_data: AdCarIdInput,
        api_key: str = Depends(check_api_key, use_cache=True),
    ):

        # ================== Checking Valid ObjectId for Car ID ==================

        # Check if car_id is a valid MongoDB ObjectId
        if not ObjectId.is_valid(car_data.carid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid car_id. Must be a valid MongoDB ObjectId.",
            )

        # ======================= Checking if UserID is in Database or not =======================

        # Check if user_id exists in the database
        if not carzcollection.find_one({"_id": ObjectId(car_data.carid)}):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Car ID not found in database.",
            )

        # ======================= Ad Checking =======================

        try:
            start_time = time.time()
            car_ad_score = carAdMain(car_data.carid)
            end_time = time.time()

            total_time = end_time - start_time
            print("Time taken total: ", total_time)
            # car_ad_score = dummy(car_data.carid)
            return car_ad_score

        except Exception as e:
            # Handle exceptions, log them, and return an appropriate response
            raise HTTPException(status_code=500, detail="Internal Server Error") from e
    
    if __name__ == "__main__":
        uvicorn.run(app, host="127.0.0.1", port=80)


except Exception as e:
    print(e)
