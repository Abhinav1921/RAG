# API Documentation - User Management Service

## Introduction
The User Management Service provides RESTful APIs for user authentication, authorization, and profile management. This service is built using Node.js and Express.js framework.

## Base URL
https://api.techcorp.com/v1/users

## Authentication
All API requests require an API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Create User
**POST /users**

Creates a new user account.

Request Body:
```json
{
  "username": "string (required)",
  "email": "string (required)",
  "password": "string (required, min 8 chars)",
  "firstName": "string (required)",
  "lastName": "string (required)",
  "role": "string (optional, default: user)"
}
```

Response (201 Created):
```json
{
  "id": "user_12345",
  "username": "johndoe",
  "email": "john@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "role": "user",
  "createdAt": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

### Get User
**GET /users/{userId}**

Retrieves user information by ID.

Parameters:
- userId (path): The unique user identifier

Response (200 OK):
```json
{
  "id": "user_12345",
  "username": "johndoe",
  "email": "john@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "role": "user",
  "lastLogin": "2024-01-15T14:22:00Z",
  "status": "active"
}
```

### Update User
**PUT /users/{userId}**

Updates user profile information.

Request Body:
```json
{
  "firstName": "string (optional)",
  "lastName": "string (optional)",
  "email": "string (optional)"
}
```

### Delete User
**DELETE /users/{userId}**

Soft deletes a user account (sets status to inactive).

Response (204 No Content)

### List Users
**GET /users**

Retrieves a paginated list of users.

Query Parameters:
- page (integer): Page number (default: 1)
- limit (integer): Items per page (default: 20, max: 100)
- role (string): Filter by user role
- status (string): Filter by user status

## Error Codes
- 400: Bad Request - Invalid input data
- 401: Unauthorized - Invalid or missing API key
- 403: Forbidden - Insufficient permissions
- 404: Not Found - User not found
- 409: Conflict - Username or email already exists
- 422: Unprocessable Entity - Validation errors
- 500: Internal Server Error - Server-side error

## Rate Limiting
API calls are limited to 1000 requests per hour per API key. Headers include:
- X-RateLimit-Limit: 1000
- X-RateLimit-Remaining: 999
- X-RateLimit-Reset: 1642248000

## SDKs and Libraries
Official SDKs available for:
- JavaScript/Node.js
- Python
- Java
- C#/.NET

For support, contact api-support@techcorp.com