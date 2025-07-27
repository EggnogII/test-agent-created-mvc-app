# Vehicle Decoder Application

This repository contains a simple web application that decodes vehicle
information from a VIN (Vehicle Identification Number) or a licence
plate.  When a VIN is supplied, the application calls the public
**NHTSA vPIC API** to return details about the vehicle.  When a plate
and state/province are supplied, the application can optionally call
the **CarsXE Plate Decoder API** if you configure an API key.  The
application is containerised with Docker and the Terraform
configuration in the `terraform` directory can be used to deploy it
to AWS using Fargate and an Application Load Balancer.

## Features

* **Decode VINs via the NHTSA API:** The app queries the NHTSA
  `DecodeVinValues` endpoint to obtain decoded vehicle attributes.  The
  vPIC documentation notes that `DecodeVinValues` returns flat key‑value
  pairs in JSON and supports optional `modelyear` query parameters
  【311902232095331†L68-L99】.
* **Decode licence plates via CarsXE (optional):** If you set
  `CARSXE_API_KEY` in the environment the app will make an HTTP GET
  request to `http://api.carsxe.com/platedecoder` with the `plate`,
  `state`, `format=json` and `key` parameters.  The CarsXE tutorial
  highlights that these parameters are required to successfully call
  the endpoint【545417615960480†L75-L86】.
* **Single‑page form:** A simple HTML form allows the user to enter
  either a VIN or a licence plate and state/province.  Results are
  displayed in JSON format.
* **Containerised:** A `Dockerfile` is provided to build a lightweight
  image based on Python 3.10.
* **Infrastructure as Code:** Terraform scripts create an ECR
  repository, Fargate cluster and service, an Application Load
  Balancer, CloudWatch log group and the necessary IAM roles and
  security groups.

## Local Development

1. **Install dependencies:** It is recommended to create a virtual
   environment first.

   ```bash
   cd vehicle_decoder
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the app locally:**

   ```bash
   # Optionally export an API key for plate decoding
   export CARSXE_API_KEY=your_carsxe_api_key
   python app.py
   ```

   The application will start on `http://localhost:5000`.

## Building and Running with Docker

To build the Docker image and run it locally:

```bash
cd vehicle_decoder
docker build -t vehicle-decoder:latest .
docker run -p 5000:5000 \
  -e CARSXE_API_KEY=your_carsxe_api_key \
  vehicle-decoder:latest
```

Navigate to `http://localhost:5000` in a browser to use the app.

## Deploying to AWS with Terraform

The Terraform configuration in the `terraform` directory sets up the
necessary AWS resources to run the container on ECS Fargate behind an
Application Load Balancer (HTTP only).  Before running Terraform you
must build your Docker image, push it to ECR and provide the image
URI.  The steps below assume you have configured AWS credentials via
the AWS CLI or environment variables and have [Terraform installed](https://www.terraform.io/downloads.html).

1. **Initialize an ECR repository:**

   Run Terraform once with only the `ecr_repository` resource to
   create the repository.  From within the `terraform` directory:

   ```bash
   cd vehicle_decoder/terraform
   terraform init
   terraform apply -target=aws_ecr_repository.this -auto-approve
   ```

   After applying, note the ECR repository URI in the Terraform
   output or find it in the AWS console.

2. **Build and push the Docker image:**

   Tag the image with the repository URI returned above (replace
   `ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/vehicle-decoder-repo` with
   your actual URI and choose a tag such as `v1`):

   ```bash
   # Authenticate Docker to ECR
   aws ecr get-login-password --region us-west-2 | \
     docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com

   # Build and tag
   docker build -t vehicle-decoder:latest ../..
   docker tag vehicle-decoder:latest ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/vehicle-decoder-repo:v1

   # Push
   docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/vehicle-decoder-repo:v1
   ```

3. **Deploy the infrastructure:**

   Create a `terraform.tfvars` file in the `terraform` directory to set
   the required variables:

   ```hcl
   # terraform.tfvars
   prefix        = "vehicle-decoder"
   image_url     = "ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/vehicle-decoder-repo:v1"
   carsxe_api_key = "" # optional: set your API key here or leave blank
   desired_count = 2    # adjust as needed
   ```

   Then apply the full configuration:

   ```bash
   terraform apply
   ```

   Terraform will provision a new ECS cluster, Fargate service, load
   balancer and related resources.  At the end of the run it will
   output the DNS name of the load balancer under `load_balancer_dns`.

4. **Access your application:**

   Visit `http://<load_balancer_dns>` in your web browser.  You should
   see the Vehicle Decoder form and be able to decode VINs (and
   licence plates if an API key is configured).

## Customisation

* **CarsXE API key:** To enable licence plate decoding, sign up for a
  CarsXE account and obtain an API key.  Pass this key via the
  `carsxe_api_key` Terraform variable or set the `CARSXE_API_KEY`
  environment variable when running locally.
* **Scaling:** Adjust `desired_count`, `ecs_task_cpu`, and
  `ecs_task_memory` in `terraform.tfvars` to scale the service.

## Caveats

* The CarsXE Plate Decoder API requires an API key and may charge
  per‑request fees.  The provided code will gracefully handle
  situations where the key is omitted by returning a user‑friendly
  error message.
* The NHTSA vPIC API is public and free to use but is subject to
  rate limits.  Refer to NHTSA documentation for details【311902232095331†L68-L99】.
