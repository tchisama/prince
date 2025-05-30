# HTML to PDF Converter API

A Python Flask API that converts HTML to PDF using Prince XML.

## Features

- Convert HTML content to PDF via POST request
- Support for both raw HTML and JSON payloads
- Built-in validation and error handling
- Health check endpoint
- Automatic cleanup of temporary files
- Configurable file size limits

## Prerequisites

- Python 3.7+
- Prince XML installed and available in PATH
- Flask and dependencies (see requirements.txt)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Prince XML is installed and accessible:
```bash
prince --version
```

## Usage

### Start the API Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### POST /convert
Convert HTML to PDF

**Request formats:**

1. **Raw HTML in body:**
```bash
curl -X POST http://localhost:5000/convert \
  -H "Content-Type: text/html" \
  -d '<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>' \
  --output output.pdf
```

2. **JSON payload:**
```bash
curl -X POST http://localhost:5000/convert \
  -H "Content-Type: application/json" \
  -d '{"html": "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>"}' \
  --output output.pdf
```

**Response:**
- Success: PDF file (application/pdf)
- Error: JSON with error message

#### GET /health
Check API health and Prince XML availability

```bash
curl http://localhost:5000/health
```

#### GET /
Get API information and usage examples

```bash
curl http://localhost:5000/
```

## Configuration

- **Port:** 5000 (default)
- **Max file size:** 16MB
- **Timeout:** 30 seconds for PDF conversion
- **Host:** 0.0.0.0 (accepts connections from any IP)

## Error Handling

The API handles various error conditions:

- Invalid HTML content
- Missing request body
- Prince XML conversion failures
- File size limits exceeded
- Conversion timeouts

All errors return appropriate HTTP status codes and JSON error messages.

## Postman Testing

### POST /convert (Raw HTML)
- **Method:** POST
- **URL:** `http://localhost:5000/convert`
- **Headers:** `Content-Type: text/html`
- **Body:** Raw HTML content
- **Response:** PDF file download

### POST /convert (JSON)
- **Method:** POST
- **URL:** `http://localhost:5000/convert`
- **Headers:** `Content-Type: application/json`
- **Body:** `{"html": "<!DOCTYPE html><html>...</html>"}`
- **Response:** PDF file download

### GET /health
- **Method:** GET
- **URL:** `http://localhost:5000/health`
- **Response:** JSON status

## Security Notes

- The API accepts HTML from any source - validate input in production
- Consider implementing authentication for production use
- File size limits help prevent abuse
- Temporary files are automatically cleaned up
