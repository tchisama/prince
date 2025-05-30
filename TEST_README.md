# Raw HTML Conversion Testing Tool with Analytics

A focused testing tool for the HTML to PDF Converter API that specifically tests the raw HTML conversion endpoint with large-scale request analytics.

## Features

- 🎯 **Focused Testing**: Tests only the raw HTML conversion endpoint (`POST /convert`)
- 📊 **Large-Scale Analytics**: Detailed statistics for high-volume testing
- 🏃‍♂️ **High-Volume Testing**: Support for hundreds or thousands of requests
- 📈 **Advanced Metrics**: Percentiles, standard deviation, throughput analysis
- 📄 **File Size Analysis**: PDF generation metrics and compression ratios
- 💾 **JSON Export**: Save analytics data for further analysis
- 🎯 **Custom HTML Testing**: Test with your own HTML files
- 📱 **Real-time Progress**: Live progress updates for large test runs

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your API server is running:
```bash
python app.py
```

## Usage

### Basic Large-Scale Testing

Run 100 raw HTML conversion requests (default):
```bash
python test_api.py
```

### Custom Number of Requests

Test with a specific number of requests:
```bash
python test_api.py --requests 500
```

### High-Volume Testing

Test with thousands of requests:
```bash
python test_api.py --requests 1000
```

### Custom API URL

Test against a different server:
```bash
python test_api.py --url http://your-server:5000 --requests 200
```

### Save Analytics to JSON

Export detailed analytics to a JSON file:
```bash
python test_api.py --requests 300 --save-json
```

### Test Custom HTML

Test with your own HTML file:
```bash
python test_api.py --html-file sample_test.html
```

### Combined Options

```bash
python test_api.py --url http://localhost:5000 --requests 1000 --save-json
```

## Test Focus

The tool focuses specifically on:

**Raw HTML Conversion** (`POST /convert`)
- Tests HTML to PDF conversion via raw HTML body
- Sends HTML content with `Content-Type: text/html`
- Validates PDF generation and response handling
- Measures conversion time and PDF file size
- Runs the same test multiple times for statistical analysis

### Test HTML Content

Each request sends a well-formed HTML document containing:
- Proper DOCTYPE declaration
- CSS styling for visual formatting
- Dynamic timestamp for uniqueness
- Structured content (headers, paragraphs)

This ensures consistent testing while providing realistic conversion scenarios.

## Analytics Output

The tool provides comprehensive analytics including:

### Test Summary
- Total requests executed
- Success/failure counts
- Overall success rate
- Total test duration

### Advanced Performance Metrics
- Average response time
- Fastest/slowest response times
- Median response time
- **Standard deviation** (consistency measure)
- **95th percentile** (performance under load)
- **99th percentile** (worst-case scenarios)

### Throughput Analysis
- **Total duration** of all requests
- **Requests per second** (throughput rate)
- Performance consistency over time

### Error Analysis
- Common error patterns
- Error frequency counts
- Failure rate analysis

### File Size Analysis
- PDF generation statistics
- Average file sizes (HTML vs PDF)
- Compression ratios
- Data transfer efficiency

## Sample Output

```
🏃‍♂️ Running Large-Scale Raw HTML Test (500 requests)...
🚀 Starting Raw HTML Conversion Tests...
📍 Target URL: http://localhost:5000
🔢 Number of requests: 500
============================================================

✅ PASS | Valid HTML (Raw) | 200 | 324.56ms
✅ PASS | Valid HTML (Raw) | 200 | 298.23ms
✅ PASS | Valid HTML (Raw) | 200 | 312.45ms
Progress: 10/500 requests completed...
Progress: 20/500 requests completed...
...
Progress: 500/500 requests completed...

============================================================
✅ All 500 tests completed!

📊 TEST ANALYTICS REPORT
================================================================================

📋 TEST SUMMARY:
   Total Tests: 500
   Successful: 487 ✅
   Failed: 13 ❌
   Success Rate: 97.40%
   Duration: 0:02:45.123456

⚡ PERFORMANCE METRICS:
   Average Response Time: 298.45ms
   Fastest Response: 156.23ms
   Slowest Response: 1245.67ms
   Median Response Time: 287.34ms
   Standard Deviation: 89.12ms
   95th Percentile: 456.78ms
   99th Percentile: 892.34ms

🚀 THROUGHPUT METRICS:
   Total Duration: 165.12s
   Requests per Second: 3.03

📄 FILE SIZE ANALYSIS:
   PDFs Generated: 487
   Avg PDF Size: 45.67 KB
   Avg HTML Size: 2.34 KB
   Compression Ratio: 19.51x
```

## Integration with Postman

The tool is designed to complement Postman testing:

1. **Use the analytics** to identify performance bottlenecks
2. **Export JSON data** for detailed analysis in Postman
3. **Test custom HTML** files before importing to Postman
4. **Validate API behavior** before creating Postman collections

## Files Generated

- `test_analytics_YYYYMMDD_HHMMSS.json`: Detailed analytics data
- `test_output_YYYYMMDD_HHMMSS.pdf`: Generated PDF files from tests

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the API server is running
   - Check the URL and port

2. **Prince XML Not Found**
   - Install Prince XML on your system
   - Verify Prince XML is in your PATH

3. **Timeout Errors**
   - Increase timeout values for large documents
   - Check server performance

### Debug Mode

For detailed debugging, modify the script to add more logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Feel free to extend the testing scenarios or analytics features:

1. Add new test methods to the `APITester` class
2. Extend analytics in the `generate_analytics()` method
3. Add new command-line options in the `main()` function

## License

This testing tool is provided as-is for development and testing purposes.
