# 📸 Media Service API Documentation

This document provides usage instructions for the Media Service APIs.  
These APIs allow you to **upload images, list them, view/download, and delete** images.  
They are backed by API Gateway, Lambda, S3, and DynamoDB.

---

## 🔑 Authentication

All requests (except direct signed URL usage) require a **Bearer JWT token** in the `Authorization` header.

Example:
```
Authorization: Bearer <your_token>
```

---

## 1. Upload Image (Fetch Upload Signed URL)

**Endpoint**:  
`POST {{base_url}}/upload`

**Headers**:
- `Authorization: Bearer {{token}}`
- `Content-Type: application/json`

**Body**:
```json
{
  "contentType": "image/jpeg"
}
```

**Sample Response**:
```json
{
  "uploadUrl": "http://localhost:4566/media-bucket/123/fd984949-6200-4e64-9ad9-5c6d6040a3dd?...",
  "mediaId": "fd984949-6200-4e64-9ad9-5c6d6040a3dd",
  "requestId": "934df410-7709-4d5e-83e3-c100cea062c4",
  "userId": "123"
}
```

---

## 2. Upload Image File

Use the **presigned URL** received from step 1.

**Endpoint**:  
`PUT {{presigned_url}}`

**Headers**:
- `Content-Type: image/jpeg`

**Body**: Binary image file (`image.jpg`).

**Sample Success Response**:  
`200 OK` (empty body)

---

## 3. List All Images

**Endpoint**:  
`GET {{base_url}}/list`

**Headers**:
- `Authorization: Bearer {{token}}`
- `Content-Type: application/json`

**Sample Response**:
```json
{
  "items": [
    {
      "SK": "media#fd984949-6200-4e64-9ad9-5c6d6040a3dd",
      "s3Key": "123/fd984949-6200-4e64-9ad9-5c6d6040a3dd",
      "PK": "user#123",
      "requestId": "934df410-7709-4d5e-83e3-c100cea062c4",
      "status": "COMPLETED"
    }
  ],
  "requestId": "934df410-7709-4d5e-83e3-c100cea062c4"
}
```

---

## 4. View Image (Get Presigned Download URL)

**Endpoint**:  
`GET {{base_url}}/view/{{mediaId}}`

**Headers**:
- `Authorization: Bearer {{token}}`

**Sample Response**:
```json
{
  "downloadUrl": "http://localhost:4566/media-bucket/123/2eec835c-54ac-4edf-92ec-914fa8c0bf0e?...",
  "requestId": "934df410-7709-4d5e-83e3-c100cea062c4"
}
```

---

## 5. Download Image

**Endpoint**:  
`GET {{downloadUrl}}`  

This URL is temporary (presigned) and **does not require Authorization header**.

**Command Example**:
```bash
curl -o downloaded.jpg "{{downloadUrl}}"
```

---

## 6. Delete Image

**Endpoint**:  
`DELETE {{base_url}}/delete/{{mediaId}}`

**Headers**:
- `Authorization: Bearer {{token}}`
- `Content-Type: application/json`

**Sample Response**:
```json
{
  "message": "Deleted 123/2eec835c-54ac-4edf-92ec-914fa8c0bf0e",
  "requestId": "934df410-7709-4d5e-83e3-c100cea062c4"
}
```

---

## 🌐 Variables

- `base_url`: Base API URL (example: `http://127.0.0.1:3000`)
- `token`: Your JWT authentication token
- `contentType`: Image content type (default: `image/jpeg`)
- `presigned_url`: Upload URL from step 1
- `downloadUrl`: Download URL from step 4
- `mediaId`: Unique image identifier

---

## ⚡ Usage Flow

1. **Upload signed URL** → Fetch presigned URL and `mediaId`
2. **Upload file** → Use the signed URL to PUT the image
3. **List images** → Get list of images uploaded
4. **View image** → Get signed download URL
5. **Download** → Fetch the image directly
6. **Delete** → Delete image from S3 and DynamoDB

