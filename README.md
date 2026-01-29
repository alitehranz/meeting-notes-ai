# AI Meeting Notes Analyzer

A full-stack web application that automatically extracts action items, decisions, and key discussion points from meeting notes using artificial intelligence.

## Overview

This application addresses a common business problem: after meetings, notes are unstructured and action items get lost. The AI Meeting Notes Analyzer processes raw meeting notes and automatically organizes them into actionable components, improving team accountability and follow-through.

## Core Features

- AI-powered extraction of action items with assigned personnel and deadlines
- Automatic identification of key decisions made during meetings
- Extraction of important discussion points
- Generated meeting summaries for quick reference
- Persistent storage of all meetings and extracted data
- Clean, responsive web interface

## Technology Stack

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy - Database ORM and toolkit
- SQLite - Lightweight relational database
- Claude AI via OpenRouter - Natural language processing
- Pydantic - Data validation and serialization

### Frontend
- HTML5/CSS3 - Semantic markup and styling
- Vanilla JavaScript - Client-side logic
- Responsive design - Mobile and desktop support

### Infrastructure
- Python virtual environment for dependency isolation
- Environment-based configuration
- CORS middleware for cross-origin requests

## Architecture

The application follows a three-tier architecture:

1. Presentation Layer: Single-page web application with form input and results display
2. Application Layer: RESTful API built with FastAPI handling business logic
3. Data Layer: SQLite database with relational schema for meetings, action items, decisions, and key points

### Request Flow

1. User submits meeting title and notes via web form
2. Frontend sends POST request to /api/meetings endpoint
3. Backend validates input and forwards notes to Claude AI
4. AI returns structured JSON with extracted data
5. Backend persists meeting and related entities to database
6. Frontend fetches complete meeting details and displays formatted results

### Database Schema

**Meetings Table**
- Primary key (id)
- Meeting metadata (title, date, created_at)
- Raw notes text
- AI-generated summary

**Action Items Table**
- Foreign key to meetings table
- Task description
- Assigned person
- Deadline
- Status tracking

**Decisions Table**
- Foreign key to meetings table
- Decision text
- Timestamp

**Key Points Table**
- Foreign key to meetings table
- Discussion point text
- Timestamp

## Installation and Setup

### Prerequisites
- Python 3.13 or higher
- OpenRouter API key for AI access

### Steps

1. Clone this repository
2. Create and activate virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Create .env file in project root with:
```
   OPENROUTER_API_KEY=your_api_key_here
```
5. Start backend server:
```bash
   python -m app.main
```
6. In a separate terminal, start frontend server:
```bash
   cd frontend
   python3 -m http.server 3000
```
7. Access application at http://localhost:3000

## API Documentation

### Create Meeting
**POST** /api/meetings

Request body:
```json
{
  "title": "string",
  "raw_notes": "string"
}
```

Response:
```json
{
  "meeting_id": "integer",
  "title": "string",
  "summary": "string",
  "date": "datetime",
  "action_items_count": "integer",
  "message": "string"
}
```

### Get All Meetings
**GET** /api/meetings

Returns list of all meetings with metadata and action item counts.

### Get Meeting Details
**GET** /api/meetings/{meeting_id}

Returns complete meeting data including all action items, decisions, and key points.

### Get All Action Items
**GET** /api/action-items

Returns all action items across all meetings with meeting context.

### Complete Action Item
**PATCH** /api/action-items/{item_id}/complete

Marks an action item as completed.

## Technical Decisions

### Why Claude AI?
Claude 3 Haiku offers fast inference times (2-3 seconds), excellent structured data extraction capabilities, and cost-effective pricing at $0.25 per million tokens. The model consistently produces valid JSON responses with minimal parsing errors.

### Why FastAPI?
FastAPI provides automatic OpenAPI documentation, native async support, and built-in data validation via Pydantic. Development velocity is high due to minimal boilerplate and strong typing support.

### Why SQLite?
SQLite requires zero configuration, is perfect for portfolio demonstrations, and can easily scale to thousands of meetings. Migration to PostgreSQL or MySQL is straightforward if needed for production deployment.

### Why Vanilla JavaScript?
Using vanilla JavaScript demonstrates core language proficiency without framework overhead. The application loads faster, has no build tooling complexity, and is easier for technical reviewers to evaluate.

## Security Considerations

- API keys stored in environment variables, never committed to version control
- CORS configured with explicit allowed origins
- SQL injection prevention via SQLAlchemy ORM
- Input validation on both frontend and backend
- Error messages sanitized to avoid exposing internal details

## Cost Analysis

- Initial credit: $5 on OpenRouter
- Per-request cost: Approximately $0.0003
- Request capacity: Over 1,500 meeting analyses with initial credit
- Scalability: Supports meeting notes up to 1,000+ words efficiently

## Future Enhancements

Potential features for future development:
- User authentication and multi-tenant support
- Export functionality for PDF and CSV formats
- Calendar integration for deadline management
- Email notifications for pending action items
- Team collaboration features
- Analytics dashboard with insights
- Browser extension for quick capture



## Skills Demonstrated

- Full-stack web development
- RESTful API design and implementation
- Database modeling and relationships
- Third-party API integration
- Asynchronous programming
- Error handling and validation
- Environment-based configuration
- Responsive web design
- Code documentation and architecture

## License

This project is a portfolio demonstration and is available for educational purposes.

## Author

Built as a portfolio project demonstrating full-stack development capabilities for 2026 internship applications.


## Known Limitations
- Single-user system (no auth yet)
- SQLite not ideal for production-scale concurrent writes
- AI output quality depends on input clarity
