# Gmail Integration with AWS S3

## Overview
This project demonstrates a Flask-based application for integrating Gmail with AWS S3. It enables users to fetch Gmail emails based on dynamic filters, process attachments, and upload them to an S3 bucket. The app uses Google OAuth2 for authentication and the Gmail API to interact with user emails.

## Features
- **Google OAuth2 Authentication**: Securely login to Gmail using OAuth2.
- **Fetch Emails**: Retrieve Gmail emails based on dynamic filters (e.g., subject, sender, keyword, date range).
- **Process Attachments**: Extract and upload email attachments to an AWS S3 bucket.
- **AWS S3 Integration**: Securely upload files to an S3 bucket with configurable credentials.

## Prerequisites
1. **Python**: Version 3.7 or higher.
2. **Google Cloud Console**: A project with Gmail API enabled and a downloaded `client_secret.json` file.
3. **AWS Account**: An S3 bucket and access credentials.
4. **Environment Variables**:
   - `CLIENT_SECRET_FILE`: Path to the `client_secret.json` file.
   - `S3_BUCKET`: Name of your S3 bucket.
   - `AWS_ACCESS_KEY`: Your AWS Access Key.
   - `AWS_SECRET_KEY`: Your AWS Secret Key.

## Setup Instructions

### 1. Clone the Repository
```bash
$ git clone <repository_url>
$ cd <repository_directory>
```

### 2. Create a Virtual Environment
```bash
$ python3 -m venv venv
$ source venv/bin/activate  # For Linux/Mac
$ venv\Scripts\activate   # For Windows
```

### 3. Install Dependencies
```bash
$ pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project directory and add:
```env
CLIENT_SECRET_FILE=path/to/your/client_secret.json
S3_BUCKET=your-s3-bucket-name
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=""
```

### 5. Run the Application
```bash
$ flask run
$ python app.py
```

The app will start at `http://localhost:5000`.

## API Endpoints

### 1. **Login**
- **URL**: `/api/login`
- **Method**: `GET`
- **Description**: Redirects the user to Google OAuth2 login.

### 2. **OAuth Callback**
- **URL**: `/api/oauth/callback`
- **Method**: `GET`
- **Description**: Handles the OAuth2 callback and stores user tokens in the session.

### 3. **Fetch Emails**
- **URL**: `/api/fetch-emails`
- **Method**: `GET`
- **Query Parameters**:
  - `subject`: Filter emails by subject.
  - `from`: Filter emails by sender.
  - `keyword`: Search for specific keywords in emails.
  - `after`: Filter emails after a specific date (YYYY/MM/DD).
  - `before`: Filter emails before a specific date (YYYY/MM/DD).

### 4. **Fetch Emails with Attachments**
- **URL**: `/api/fetch-emails-with-attachments`
- **Method**: `GET`
- **Query Parameters**:
  - Same as `/api/fetch-emails`.
- **Description**: Fetch emails based on filters and upload their attachments to S3.

## How It Works
1. **Authentication**: Users log in via Google OAuth2 to grant access to their Gmail.
2. **Fetch Emails**: Emails are fetched using the Gmail API based on user-defined filters.
3. **Process Attachments**: Attachments are extracted, decoded, and uploaded to the specified S3 bucket.
4. **S3 Integration**: Files are securely uploaded to S3 using Boto3.

## Troubleshooting
- **Access Denied for S3 Objects**:
  - Ensure the S3 bucket policy allows public access or use pre-signed URLs for controlled access.
  - Check the bucket’s Block Public Access settings.
- **No Emails Found**:
  - Verify the filters used in the query.
  - Ensure the Gmail account has emails matching the criteria.
- **Invalid OAuth2 Credentials**:
  - Ensure the `client_secret.json` file is correctly configured.

## Security Best Practices
1. **Environment Variables**: Store sensitive information like AWS keys and client secrets in a `.env` file.
2. **IAM Roles**: Use IAM roles for granular permissions instead of root AWS credentials.
3. **HTTPS**: Deploy the application behind an HTTPS proxy for secure communication.
4. **Session Management**: Regularly clear expired tokens from the session.

## Dependencies
- Flask
- Google API Client
- Boto3
- Dotenv

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

Happy Coding!

