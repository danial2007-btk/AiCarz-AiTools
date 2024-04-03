from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    Depends,
    Query,
    status,
    Request,
)
from pydantic import BaseModel, validator
from tireTrade import preprocess_image, predict_image
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from memory_profiler import profile
from PIL import Image, ImageDraw
from bson import ObjectId
import psutil
import asyncio
import uvicorn
import time
import io

from main import carAdMain
from bodyPannel import model
from mongodb import carzcollection, mongodbConn

try:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load the ML model
        print("======> loading statup event")
        yield
        # Clean up the ML models and release the resources
        print("xxxxxxxx shurting down event")
        mongodbConn.close()
        print("mongodb disconnected")
    
    class CatchLargeUploadMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Attempt to catch large uploads
            if "content-length" in request.headers:
                content_length = int(request.headers["content-length"])
                max_size = 100 * 1024 * 1024  # 100 MB
                if content_length > max_size:
                    return JSONResponse(
                        status_code=413,
                        content={"message": "Please upload a file of maximum 5 MB."},
                    )
            response = await call_next(request)
            return response

    # The valid API key
    API_key = "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"

    # Dependency to check API key
    def check_api_key(api_key: str = Query(..., description="API Key")):
        if api_key != API_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return api_key
    
    app = FastAPI(lifespan=lifespan)
    # Add the middleware to the application
    app.add_middleware(CatchLargeUploadMiddleware)
    
    # Define a function to log memory consumption
    async def log_memory_consumption():
        while True:
            mem_info = psutil.virtual_memory()
            print(f"Memory Usage: {mem_info.used / (1024*1024):.2f} MB")
            await asyncio.sleep(60)  # Log memory consumption every minute

    @app.on_event("startup")
    async def startup_event():
        # Start the memory consumption logging coroutine on startup
        asyncio.create_task(log_memory_consumption())
    # ########################################       APP CHECKING         ########################################

    # Root Endpoint
    @app.get("/")
    def read_root():
        return {"message": "App is running successfully"}

    # ########################################       Car AD Checker API ENDPOINT         ########################################

    class AdCarIdInput(BaseModel):
        carid: str  # Car ID as input

    # car AdChecking API Endpoint
    @profile
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

    # ########################################       Car Tyre Tread Checker API ENDPOINT         ########################################

    # Define a BaseModel for the file upload request
    class FileUpload(BaseModel):
        file: UploadFile

        # Custom validator to check file format
        @validator("file")
        def check_file_format(cls, v):
            allowed_formats = ["image/png", "image/jpeg", "image/jpg"]
            if v.content_type not in allowed_formats:
                raise ValueError(
                    "Invalid file type: Only PNG, JPG, and JPEG are allowed."
                )
            return v
    
    @profile
    @app.post("/tirechecker")
    async def tirechecker(
        file: UploadFile = File(...),
        api_key: str = Depends(check_api_key, use_cache=True),
    ):
        try:
            # Read image file
            contents = await file.read()

            # Preprocess the image
            img_array = preprocess_image(contents)

            # Make prediction
            result = predict_image(img_array)

            return {"result": result}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ########################################       Car Body Panel Checker API ENDPOINT         ########################################
    @profile
    @app.post("/bodyPannel")
    async def bodyPannel(
        file: UploadFile = File(...),
        api_key: str = Depends(check_api_key, use_cache=True),
    ):
        
        # Ensure that a file is uploaded
        if file is None:
            return {"error": "No file uploaded."}

        # # Convert the uploaded file to a PIL Image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Perform prediction
        results = model().predict(image, conf=0.50)

        # Get bounding boxes from results
        boxes = results[0].boxes.xyxy  

        # Draw bounding boxes on the image
        draw = ImageDraw.Draw(image)
        line_width = 8
        for box in boxes:
            draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="red", width=line_width)

        # Save the modified image to a bytes buffer
        buf = io.BytesIO()
        image.save(buf, format='JPEG')
        buf.seek(0)

        # Return the modified image directly
        return StreamingResponse(buf, media_type="image/jpeg")
    
    
    if __name__ == "__main__":
        uvicorn.run(app, host="127.0.0.1", port=8080)


except Exception as e:
    print("Error inside the MAIN API FILE:", e)
