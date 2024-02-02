# Stage 1: Build environment
FROM python:3.9 AS builder

# Set the working directory
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv /app/aitools

# Activate the virtual environment
ENV PATH="/app/aitools/bin:$PATH"

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app/aitools /app/aitools
COPY . .

# Expose the port on which your FastAPI app will run
EXPOSE 80

# Command to run your FastAPI application
CMD ["/app/aitools/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
