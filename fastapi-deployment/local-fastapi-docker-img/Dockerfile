# Use a standard Python image instead of AWS Lambda
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy application files
COPY ./app /app

# Copy and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the API port
EXPOSE 8080

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
