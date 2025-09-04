# scripts/create_sample_documents.py
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def create_sample_documents():
    """Create sample documents for testing"""
    
    # Create a documents folder if it doesn't exist
    docs_folder = Path(__file__).parent.parent / "sample_documents"
    docs_folder.mkdir(exist_ok=True)
    
    # Sample Document 1: Company Policy
    policy_content = """
# Company Remote Work Policy

## Overview
This document outlines the remote work policy for employees of TechCorp Inc. Our goal is to provide flexibility while maintaining productivity and collaboration.

## Eligibility
All full-time employees who have completed their probationary period are eligible for remote work arrangements. Part-time employees may be considered on a case-by-case basis.

## Work Schedule
Remote workers are expected to maintain core business hours from 9 AM to 3 PM in their local time zone. Outside these hours, flexible scheduling is permitted with manager approval.

## Equipment and Technology
The company will provide necessary equipment including:
- Laptop computer
- External monitor
- Ergonomic desk setup allowance up to $500
- Internet connectivity reimbursement up to $50/month

## Communication Requirements
Remote workers must:
- Attend all scheduled team meetings via video conference
- Respond to messages within 4 hours during business hours
- Use company-approved communication tools (Slack, Microsoft Teams)
- Maintain regular check-ins with their direct manager

## Performance Expectations
Performance will be measured by results and deliverables, not hours worked. Key performance indicators include:
- Meeting project deadlines
- Quality of work output
- Participation in team activities
- Customer satisfaction ratings

## Security Requirements
All remote workers must:
- Use company VPN for accessing internal systems
- Keep software and systems updated
- Report security incidents immediately
- Follow data protection protocols
- Use encrypted storage for sensitive information

## Workspace Requirements
Home office must have:
- Reliable high-speed internet connection
- Quiet, distraction-free environment
- Proper lighting and ergonomic setup
- Secure location for confidential work

## Review Process
Remote work arrangements will be reviewed quarterly. Continued remote work privileges depend on maintaining performance standards and adhering to policy guidelines.

For questions about this policy, contact HR at hr@techcorp.com or call (555) 123-4567.
"""

    # Sample Document 2: Technical Documentation
    tech_doc_content = """
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
"""

    # Sample Document 3: Meeting Minutes
    meeting_content = """
# Engineering Team Meeting Minutes
Date: March 15, 2024
Time: 2:00 PM - 3:30 PM EST
Location: Conference Room B / Zoom Hybrid

## Attendees
- Sarah Johnson (Engineering Manager)
- Mike Chen (Senior Developer)
- Lisa Rodriguez (Frontend Developer)
- David Kim (Backend Developer)
- Emily Watson (DevOps Engineer)
- Alex Thompson (QA Lead)

## Agenda Items

### 1. Sprint Review - Q1 2024
**Presenter:** Sarah Johnson

Key accomplishments:
- Successfully delivered user authentication system
- Completed database migration to PostgreSQL
- Implemented new monitoring dashboard
- Fixed 23 critical bugs identified in previous sprint

Challenges faced:
- Performance issues with search functionality
- Integration delays with third-party payment processor
- Two team members on sick leave affected timeline

### 2. Technical Architecture Discussion
**Presenter:** Mike Chen

Proposed changes to improve system scalability:
- Migration from monolithic to microservices architecture
- Implementation of Redis caching layer
- Introduction of message queuing system (RabbitMQ)
- Database sharding strategy for user data

Timeline: 6-month phased approach starting April 2024

### 3. Frontend Redesign Project
**Presenter:** Lisa Rodriguez

UI/UX improvements planned:
- Modern responsive design using React 18
- Accessibility compliance (WCAG 2.1 AA)
- Dark mode implementation
- Mobile-first approach
- Component library standardization

Expected completion: June 2024

### 4. DevOps and Infrastructure
**Presenter:** Emily Watson

Infrastructure updates:
- Migration to Kubernetes orchestration
- Automated CI/CD pipeline improvements
- Security scanning integration
- Cost optimization - 30% reduction in cloud expenses
- Disaster recovery testing scheduled for April

### 5. Quality Assurance Process
**Presenter:** Alex Thompson

Testing strategy enhancements:
- Automated test coverage increased to 85%
- Performance testing integration
- Security testing protocols
- Bug tracking system optimization
- User acceptance testing procedures

## Action Items
1. Mike to create detailed microservices migration plan by March 22
2. Lisa to finalize UI mockups and user research by March 20
3. Emily to schedule infrastructure migration windows by March 18
4. David to optimize search functionality performance by March 25
5. Alex to implement new testing protocols by March 30
6. Sarah to schedule client demo for April 5

## Next Meeting
Date: March 29, 2024
Time: 2:00 PM EST
Focus: Q2 Planning and Resource Allocation

Meeting adjourned at 3:30 PM EST.
"""

    # Write the sample documents
    with open(docs_folder / "remote_work_policy.md", "w", encoding="utf-8") as f:
        f.write(policy_content.strip())
    
    with open(docs_folder / "api_documentation.md", "w", encoding="utf-8") as f:
        f.write(tech_doc_content.strip())
    
    with open(docs_folder / "meeting_minutes.md", "w", encoding="utf-8") as f:
        f.write(meeting_content.strip())
    
    print(f"✅ Sample documents created in: {docs_folder}")
    print("📄 Files created:")
    print("  - remote_work_policy.md")
    print("  - api_documentation.md") 
    print("  - meeting_minutes.md")
    print("\nYou can now upload these documents using the Streamlit app!")

if __name__ == "__main__":
    create_sample_documents()
