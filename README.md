# FastAPI Rate Limiting

This is a FastAPI application that implements rate limiting for users using Redis middleware. The application allows users to perform CRUD operations on a MongoDB database for managing student records.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

- Python 3.6 or later
- Redis
- MongoDB

### Installation

1. Clone the repo:

   ```sh
   git clone https://github.com/praveensaharan/fastapi_apis.git
   ```

2. Install requirements:

   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   ```sh
   export REDIS_HOSTNAME=<your_redis_hostname>
   export REDIS_PORT=<your_redis_port>
   export REDIS_PASSWORD=<your_redis_password>
   export MONGO_URI=<your_mongodb_uri>
   ```

4. Run the application:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000
   OR
   uvicorn main:app --reload
   ```

### Usage

    Once the application is up and running, you can access the API documentation using the following URL: [https://fastapi-apis-9j85.onrender.com/](https://fastapi-apis-9j85.onrender.com/)

#### Rate Limiting

    This application implements rate limiting for users using Redis middleware. Each user is limited to 10 requests per day. Once the limit is exceeded, a 429 Too Many Requests response is returned.

##### Each user is allowed only 10 requests per day.

#### Endpoints

    - Create Student
        ```bash
        POST /students
        ```
        Creates a new student record.

    - List Students
        ```bash
        GET /students
        ```
        Retrieves a list of students with optional filtering by country and minimum age.

    - Fetch Student
        ```bash
        GET /students/{id}
        ```
        Retrieves the details of a specific student by ID.

    - Update Student
        ```bash
        PATCH /students/{id}
        ```
        Updates the details of a specific student by ID.

    - Delete Student
        ```bash
        DELETE /students/{id}
        ```
        Deletes a specific student by ID.
