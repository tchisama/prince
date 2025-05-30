#!/usr/bin/env python3
"""
Flask API for converting HTML to PDF using Prince XML.

This API provides a POST endpoint that accepts HTML content in the request body
and returns a PDF generated using Prince XML.
"""

import os
import tempfile
import subprocess
from flask import Flask, request, send_file, jsonify
from werkzeug.exceptions import BadRequest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def validate_html(html_content):
    """
    Basic validation of HTML content.
    
    Args:
        html_content (str): HTML content to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not html_content or not isinstance(html_content, str):
        return False
    
    # Basic check for HTML structure
    html_lower = html_content.lower().strip()
    if not html_lower.startswith('<!doctype') and not html_lower.startswith('<html'):
        return False
    
    return True

def convert_html_to_pdf(html_content):
    """
    Convert HTML content to PDF using Prince XML.
    
    Args:
        html_content (str): HTML content to convert
        
    Returns:
        str: Path to the generated PDF file
        
    Raises:
        Exception: If conversion fails
    """
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as html_file:
        html_file.write(html_content)
        html_file_path = html_file.name
    
    # Create temporary PDF file
    pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    pdf_file_path = pdf_file.name
    pdf_file.close()
    
    try:
        # Run Prince XML command
        cmd = ['prince', html_file_path, '-o', pdf_file_path]
        
        logger.info(f"Running Prince XML command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Prince XML failed with return code {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            raise Exception(f"Prince XML conversion failed: {result.stderr}")
        
        # Check if PDF was created
        if not os.path.exists(pdf_file_path) or os.path.getsize(pdf_file_path) == 0:
            raise Exception("PDF file was not created or is empty")
        
        logger.info(f"PDF generated successfully: {pdf_file_path}")
        return pdf_file_path
        
    except subprocess.TimeoutExpired:
        logger.error("Prince XML conversion timed out")
        raise Exception("PDF conversion timed out")
    except Exception as e:
        logger.error(f"Error during PDF conversion: {str(e)}")
        raise
    finally:
        # Clean up HTML file
        try:
            os.unlink(html_file_path)
        except OSError:
            pass

@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    """
    Convert HTML to PDF endpoint.
    
    Expects HTML content in the request body.
    Returns PDF file as response.
    """
    try:
        # Get HTML content from request body
        if request.content_type and 'application/json' in request.content_type:
            # Handle JSON request
            data = request.get_json()
            if not data or 'html' not in data:
                return jsonify({'error': 'Missing "html" field in JSON body'}), 400
            html_content = data['html']
        else:
            # Handle raw HTML in body
            html_content = request.get_data(as_text=True)
        
        if not html_content:
            return jsonify({'error': 'Empty request body'}), 400
        
        # Validate HTML content
        if not validate_html(html_content):
            return jsonify({'error': 'Invalid HTML content'}), 400
        
        # Convert HTML to PDF
        pdf_path = convert_html_to_pdf(html_content)
        
        # Return PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name='converted.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error in convert_to_pdf: {str(e)}")
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500
    finally:
        # Clean up PDF file after sending
        try:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.unlink(pdf_path)
        except OSError:
            pass

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test if Prince XML is available
        result = subprocess.run(['prince', '--version'], capture_output=True, timeout=5)
        prince_available = result.returncode == 0
        
        return jsonify({
            'status': 'healthy',
            'prince_xml_available': prince_available
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'prince_xml_available': False
        }), 500

@app.route('/', methods=['GET'])
def index():
    """API information endpoint."""
    return jsonify({
        'name': 'HTML to PDF Converter API',
        'description': 'Convert HTML to PDF using Prince XML',
        'endpoints': {
            'POST /convert': 'Convert HTML to PDF',
            'GET /health': 'Health check',
            'GET /': 'API information'
        },
        'usage': {
            'content_type': 'text/html or application/json',
            'max_size': f'{MAX_CONTENT_LENGTH // (1024*1024)}MB',
            'example_json': {
                'html': '<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>'
            }
        }
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'error': f'File too large. Maximum size is {MAX_CONTENT_LENGTH // (1024*1024)}MB'}), 413

@app.errorhandler(400)
def bad_request(error):
    """Handle bad request error."""
    return jsonify({'error': 'Bad request'}), 400

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
