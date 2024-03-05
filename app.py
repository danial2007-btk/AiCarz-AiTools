from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO

app = FastAPI()

@app.post("/panelgap")
async def create_upload_file(file: UploadFile = File(...)):
    # Validate image format
    valid_image_types = ["image/jpeg", "image/png"]
    if file.content_type not in valid_image_types:
        raise HTTPException(status_code=400, detail="Invalid image format.")
    
    # Read the image into memory to check its size
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB in bytes
        raise HTTPException(status_code=413, detail="Image size exceeds 5MB limit.")
    
    # Since we've read the file, we need to use BytesIO to stream it back
    buffer = BytesIO(contents)
    buffer.seek(0)  # Reset the buffer's position to the beginning
    
    # Create a StreamingResponse to return the image
    return StreamingResponse(buffer, media_type=file.content_type)
