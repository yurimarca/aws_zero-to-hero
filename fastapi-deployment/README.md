## **Deployment Plan Using AWS Lambda + API Gateway**

### **1. Required AWS Services & Tools**
To deploy the FastAPI application while keeping it within AWS Free Tier limits, we will use:

1. **AWS Lambda** (for serverless hosting, Free Tier: 1M requests/month)
2. **AWS API Gateway** (to expose the FastAPI endpoints)
3. **AWS IAM** (for permissions management)
4. **AWS CloudWatch** (for monitoring logs, Free Tier: 5GB logs/month)
5. **GitHub Actions** (for CI/CD)

Required tools:
- **AWS CLI**: Install & configure (`aws configure`)
- **Docker** (optional, if packaging as a container)

---

### **2. Setting Up AWS for Deployment**
#### **A. Configure IAM Role for Lambda**
1. Go to AWS **IAM** → Click **Roles** → **Create Role**.
2. Select **Lambda** as the trusted entity.
3. Attach the following policies:
   - **AWSLambdaBasicExecutionRole** (for logging to CloudWatch)
4. Create the role and save the **Role ARN**.

#### **B. Create the AWS Lambda Function**
1. Open the AWS Lambda Console → Click **Create Function**.
2. Choose **Author from scratch**.
3. Give it a name like `fastapi-lambda`.
4. Choose **Python 3.8** as the runtime.
5. Assign the IAM Role created earlier.
6. Set the memory to **512MB** and timeout to **30 seconds**.

---

### **3. Deploying FastAPI on AWS Lambda**
FastAPI is not natively supported on AWS Lambda, so we will use **Mangum**, an adapter that allows ASGI applications to run on Lambda.

#### **A. Install Dependencies**
Update `requirements.txt`:
```txt
fastapi==0.63.0
mangum
uvicorn
```

#### **B. Modify `main.py` to Work with Lambda**
Update `starter/main.py`:

```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI app running on AWS Lambda!"}

@app.post("/predict")
def predict(data: dict):
    return {"prediction": "some result"}

handler = Mangum(app)  # Required for AWS Lambda
```

---

### **4. Deploying FastAPI to AWS Lambda**
#### **A. Package the Application**
Since AWS Lambda requires a ZIP file for deployment:

1. Create a virtual environment and install dependencies:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Create the deployment package:
   ```sh
   mkdir package
   cd package
   pip install -r ../requirements.txt -t .
   cp -r ../starter .
   zip -r9 ../fastapi_lambda.zip .
   ```
3. Upload the ZIP file to AWS Lambda:
   ```sh
   aws lambda update-function-code --function-name fastapi-lambda --zip-file fileb://fastapi_lambda.zip
   ```

---

### **5. Setting Up API Gateway**
1. Go to **AWS API Gateway** → Click **Create API**.
2. Choose **HTTP API** (cheaper than REST API).
3. Click **Add Integration** → Select **Lambda**.
4. Choose the Lambda function `fastapi-lambda`.
5. Click **Deploy** and note the **Invoke URL**.

---

### **6. Setting Up GitHub Actions for CI/CD**
Yes! You can fully automate this using **GitHub Actions**.

#### **A. Create a GitHub Actions Workflow**
Add a file `.github/workflows/deploy.yml`:

```yaml
name: Deploy FastAPI to AWS Lambda

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v2

      - name: Install Dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r starter/requirements.txt

      - name: Package Application
        run: |
          mkdir package
          cd package
          pip install -r ../starter/requirements.txt -t .
          cp -r ../starter .
          zip -r9 ../fastapi_lambda.zip .

      - name: Deploy to AWS Lambda
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: "us-east-1"
        run: |
          aws lambda update-function-code --function-name fastapi-lambda --zip-file fileb://fastapi_lambda.zip
```

#### **B. Set Up AWS Credentials in GitHub**
1. Go to **GitHub** → Your repository → **Settings** → **Secrets**.
2. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
3. Now, every time you push to `main`, GitHub Actions will package and deploy the FastAPI app to AWS Lambda.

---

### **7. Querying the Live API**
Modify `live_api_request.py`:
```python
import requests

url = "https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/"
response = requests.get(url)
print(response.json())  # Should print: {"message": "Welcome to my FastAPI app running on AWS Lambda!"}

data = {"feature1": "value"}
response = requests.post(url + "predict", json=data)
print(response.json())  # Should print: {"prediction": "some result"}
```

---

### **8. Stopping Services to Avoid Costs**
To stop billing, delete the Lambda function:
```sh
aws lambda delete-function --function-name fastapi-lambda
```
Or disable the API Gateway endpoint.

---

### **Summary of Changes**
| **Feature** | **Heroku** | **AWS Alternative** |
|------------|-----------|---------------------|
| **Hosting** | Heroku | AWS Lambda |
| **API Gateway** | Heroku Routes | AWS API Gateway |
| **CI/CD** | Heroku GitHub Deploy | GitHub Actions |
| **Storage** | Heroku Add-ons | Not Needed |
| **Logging** | Heroku Logs | AWS CloudWatch |

---

### **Final Deliverables for Rubric**
✅ **CI/CD passing screenshot** (`continuous_integration.png`)  
✅ **Live API GET Response screenshot** (`live_get.png`)  
✅ **POST Request Result screenshot** (`live_post.png`)  

---

### **What is Mangum and Why Do We Need It?**
AWS Lambda does not natively support **ASGI** applications like FastAPI. It is designed to run **WSGI-based** applications (like Flask) or direct function executions.

**Mangum** is an **ASGI adapter for AWS Lambda** that allows FastAPI (which uses ASGI) to be executed inside a Lambda function. It acts as a bridge between API Gateway and the FastAPI app.

Without **Mangum**, Lambda would not correctly handle FastAPI's request/response cycle.

### **Where Does Docker Fit into This?**
AWS Lambda has limitations on package sizes:
- If deploying code **without Docker**, the maximum package size is **50MB**.
- If deploying **with Docker**, the limit increases to **10GB**, making it ideal for ML models.

Since you are comfortable with **Docker**, we will use a **Dockerized FastAPI deployment on AWS Lambda** instead of ZIP packaging.

---

## **Deploying FastAPI on AWS Lambda with Docker**
This is the best option for **avoiding package size limits** while keeping costs minimal.

### **1. Install AWS SAM CLI**
AWS requires the **AWS Serverless Application Model (SAM)** to deploy Docker containers on Lambda.
```sh
pip install aws-sam-cli
```

---

### **2. Create the Dockerfile**
Inside the project directory, create a `Dockerfile`:
```dockerfile
# Use a minimal Python image
FROM public.ecr.aws/lambda/python:3.8

# Set the working directory
WORKDIR /var/task

# Copy the application files
COPY starter /var/task/

# Install dependencies
RUN pip install --no-cache-dir -r starter/requirements.txt

# Set the command to run FastAPI with Mangum
CMD ["starter.main.handler"]
```

### **3. Modify `main.py` for AWS Lambda**
Ensure `starter/main.py` is updated for Lambda:
```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on AWS Lambda with Docker!"}

@app.post("/predict")
def predict(data: dict):
    return {"prediction": "some result"}

# AWS Lambda handler
handler = Mangum(app)
```

---

### **4. Build and Test the Docker Container Locally**
Before deploying, test the container locally.

1. **Build the Docker Image**:
   ```sh
   docker build -t fastapi-lambda .
   ```
2. **Run the Container Locally**:
   ```sh
   docker run -p 9000:8080 fastapi-lambda
   ```
3. **Test the Local API**:
   ```sh
   curl http://localhost:9000/
   ```

---

### **5. Deploy Dockerized FastAPI to AWS Lambda**
#### **A. Authenticate AWS with Docker**
AWS Lambda uses **Elastic Container Registry (ECR)** to store container images.

1. **Authenticate Docker with AWS**:
   ```sh
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your-aws-account-id>.dkr.ecr.us-east-1.amazonaws.com
   ```
2. **Create an AWS ECR Repository**:
   ```sh
   aws ecr create-repository --repository-name fastapi-lambda
   ```
3. **Tag and Push Docker Image to ECR**:
   ```sh
   docker tag fastapi-lambda:latest <your-aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/fastapi-lambda:latest
   docker push <your-aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/fastapi-lambda:latest
   ```

#### **B. Create an AWS Lambda Function with the Docker Image**
1. Go to **AWS Lambda Console** → Click **Create Function**.
2. Select **"Container image"** as the deployment method.
3. Choose the **ECR repository** and select the `fastapi-lambda` image.
4. Set memory to **512MB**, timeout to **30s**.
5. Click **Deploy**.

---

### **6. Configure API Gateway**
1. Go to **API Gateway Console** → Click **Create API**.
2. Select **"HTTP API"** (cheaper than REST API).
3. Click **Add Integration** → Choose **Lambda**.
4. Select the `fastapi-lambda` function.
5. Click **Deploy** and note the **Invoke URL**.

---

### **7. Setting Up GitHub Actions for CI/CD**
Instead of AWS CodePipeline, we will use **GitHub Actions** to automate deployment.

#### **A. Create GitHub Actions Workflow**
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy FastAPI to AWS Lambda

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v2

      - name: Install AWS CLI
        run: |
          sudo apt-get update
          sudo apt-get install -y awscli

      - name: Install Docker CLI
        run: |
          sudo apt-get install -y docker.io

      - name: Authenticate with AWS ECR
        env:
          AWS_REGION: "us-east-1"
          AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

      - name: Build Docker Image
        run: |
          docker build -t fastapi-lambda .

      - name: Tag and Push to AWS ECR
        env:
          AWS_REGION: "us-east-1"
          AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
        run: |
          docker tag fastapi-lambda:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/fastapi-lambda:latest
          docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/fastapi-lambda:latest

      - name: Update AWS Lambda
        env:
          AWS_REGION: "us-east-1"
          AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          aws lambda update-function-code --function-name fastapi-lambda --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/fastapi-lambda:latest
```

---

### **8. Query the Live API**
Modify `live_api_request.py`:
```python
import requests

url = "https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/"
response = requests.get(url)
print(response.json())  # Should print: {"message": "Hello from FastAPI on AWS Lambda with Docker!"}

data = {"feature1": "value"}
response = requests.post(url + "predict", json=data)
print(response.json())  # Should print: {"prediction": "some result"}
```

---

### **9. Stopping Services to Avoid Costs**
To prevent AWS billing, delete the **Lambda function** and **ECR repository**:
```sh
aws lambda delete-function --function-name fastapi-lambda
aws ecr delete-repository --repository-name fastapi-lambda --force
```
Or disable API Gateway to prevent incoming traffic.

---

## **Summary of the Deployment**
| **Feature** | **AWS Service Used** |
|------------|----------------------|
| **Hosting** | AWS Lambda (Dockerized) |
| **API Gateway** | AWS API Gateway |
| **CI/CD** | GitHub Actions |
| **Container Registry** | AWS ECR |
| **Logging** | AWS CloudWatch |

---

This approach ensures:
✅ **Free-tier eligibility** (within limits)  
✅ **Minimal AWS costs** (serverless pay-per-use)  
✅ **CI/CD automation with GitHub Actions**  
✅ **Efficient deployment using Docker**  
