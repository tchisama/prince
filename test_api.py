#!/usr/bin/env python3
"""
API Testing Script with Analytics for HTML to PDF Converter

This script tests the Flask API endpoints and provides detailed analytics
including response times, success rates, and error analysis.
"""

import requests
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
import os


class APITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.session = requests.Session()

    def log_result(self, test_name: str, method: str, endpoint: str,
                   status_code: int, response_time: float,
                   success: bool, error: str = None,
                   response_size: int = 0, **kwargs):
        """Log test result for analytics"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time_ms': round(response_time * 1000, 2),
            'success': success,
            'error': error,
            'response_size_bytes': response_size,
            **kwargs
        }
        self.results.append(result)

        # Print real-time result
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name} | {status_code} | {result['response_time_ms']}ms")
        if error:
            print(f"    Error: {error}")

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("\n🔍 Testing Health Endpoint...")

        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time

            success = response.status_code == 200
            error = None if success else f"Unexpected status code: {response.status_code}"

            self.log_result(
                test_name="Health Check",
                method="GET",
                endpoint="/health",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=error,
                response_size=len(response.content),
                response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name="Health Check",
                method="GET",
                endpoint="/health",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    def test_info_endpoint(self):
        """Test the API info endpoint"""
        print("\n🔍 Testing Info Endpoint...")

        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            response_time = time.time() - start_time

            success = response.status_code == 200
            error = None if success else f"Unexpected status code: {response.status_code}"

            self.log_result(
                test_name="API Info",
                method="GET",
                endpoint="/",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=error,
                response_size=len(response.content)
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name="API Info",
                method="GET",
                endpoint="/",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    def test_convert_valid_html_json(self):
        """Test conversion with valid HTML via JSON"""
        print("\n🔍 Testing Valid HTML Conversion (JSON)...")

        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Document</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Test PDF Generation</h1>
    <p>This is a test document for PDF conversion.</p>
    <p>Current time: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
</body>
</html>"""

        payload = {"html": html_content}

        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/convert",
                json=payload,
                timeout=30
            )
            response_time = time.time() - start_time

            success = response.status_code == 200 and response.headers.get('content-type') == 'application/pdf'
            error = None
            if not success:
                if response.status_code != 200:
                    error = f"Status code: {response.status_code}"
                    try:
                        error_data = response.json()
                        error += f" - {error_data.get('error', 'Unknown error')}"
                    except:
                        error += f" - {response.text[:100]}"
                else:
                    error = f"Wrong content type: {response.headers.get('content-type')}"

            self.log_result(
                test_name="Valid HTML (JSON)",
                method="POST",
                endpoint="/convert",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=error,
                response_size=len(response.content),
                content_type=response.headers.get('content-type'),
                html_size=len(html_content)
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name="Valid HTML (JSON)",
                method="POST",
                endpoint="/convert",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    def test_convert_valid_html_raw(self):
        """Test conversion with valid HTML as raw body"""
        print("\n🔍 Testing Valid HTML Conversion (Raw)...")

        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Raw HTML Test</title>
</head>
<body>
    <h1>Raw HTML Test</h1>
    <p>This HTML was sent as raw body content.</p>
</body>
</html>"""

        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/convert",
                data=html_content,
                headers={'Content-Type': 'text/html'},
                timeout=30
            )
            response_time = time.time() - start_time

            success = response.status_code == 200 and response.headers.get('content-type') == 'application/pdf'
            error = None
            if not success:
                if response.status_code != 200:
                    error = f"Status code: {response.status_code}"
                    try:
                        error_data = response.json()
                        error += f" - {error_data.get('error', 'Unknown error')}"
                    except:
                        error += f" - {response.text[:100]}"
                else:
                    error = f"Wrong content type: {response.headers.get('content-type')}"

            self.log_result(
                test_name="Valid HTML (Raw)",
                method="POST",
                endpoint="/convert",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=error,
                response_size=len(response.content),
                content_type=response.headers.get('content-type'),
                html_size=len(html_content)
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name="Valid HTML (Raw)",
                method="POST",
                endpoint="/convert",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    def test_convert_invalid_html(self):
        """Test conversion with invalid HTML"""
        print("\n🔍 Testing Invalid HTML...")

        invalid_html = "This is not HTML content"
        payload = {"html": invalid_html}

        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/convert",
                json=payload,
                timeout=30
            )
            response_time = time.time() - start_time

            # Should return 400 for invalid HTML
            success = response.status_code == 400
            error = None if success else f"Expected 400, got {response.status_code}"

            self.log_result(
                test_name="Invalid HTML",
                method="POST",
                endpoint="/convert",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=error,
                response_size=len(response.content)
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name="Invalid HTML",
                method="POST",
                endpoint="/convert",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    def test_convert_empty_body(self):
        """Test conversion with empty body"""
        print("\n🔍 Testing Empty Body...")

        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/convert",
                data="",
                timeout=30
            )
            response_time = time.time() - start_time

            # Should return 400 for empty body
            success = response.status_code == 400
            error = None if success else f"Expected 400, got {response.status_code}"

            self.log_result(
                test_name="Empty Body",
                method="POST",
                endpoint="/convert",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=error,
                response_size=len(response.content)
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name="Empty Body",
                method="POST",
                endpoint="/convert",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e)
            )

    def test_convert_large_html(self):
        """Test conversion with large HTML content"""
        print("\n🔍 Testing Large HTML...")

        # Create a large HTML document (around 1MB)
        large_content = "<p>" + "This is a test paragraph. " * 1000 + "</p>"
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Large Document Test</title>
</head>
<body>
    <h1>Large Document Test</h1>
    {"".join([large_content for _ in range(50)])}
</body>
</html>"""

        payload = {"html": html_content}

        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/convert",
                json=payload,
                timeout=60  # Longer timeout for large content
            )
            response_time = time.time() - start_time

            success = response.status_code == 200 and response.headers.get('content-type') == 'application/pdf'
            error = None
            if not success:
                if response.status_code != 200:
                    error = f"Status code: {response.status_code}"
                    try:
                        error_data = response.json()
                        error += f" - {error_data.get('error', 'Unknown error')}"
                    except:
                        error += f" - {response.text[:100]}"
                else:
                    error = f"Wrong content type: {response.headers.get('content-type')}"

            self.log_result(
                test_name="Large HTML",
                method="POST",
                endpoint="/convert",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=error,
                response_size=len(response.content),
                html_size=len(html_content)
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name="Large HTML",
                method="POST",
                endpoint="/convert",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e),
                html_size=len(html_content)
            )

    def run_raw_html_test(self, num_requests: int = 1):
        """Run only the Valid HTML (Raw) test multiple times"""
        print("🚀 Starting Raw HTML Conversion Tests...")
        print(f"📍 Target URL: {self.base_url}")
        print(f"🔢 Number of requests: {num_requests}")
        print("=" * 60)

        # Run the raw HTML test multiple times
        for i in range(num_requests):
            if num_requests > 10 and (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/{num_requests} requests completed...")
            self.test_convert_valid_html_raw()

        print("\n" + "=" * 60)
        print(f"✅ All {num_requests} tests completed!")

    def generate_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive analytics from test results"""
        if not self.results:
            return {"error": "No test results available"}

        # Basic statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100

        # Response time statistics
        response_times = [r['response_time_ms'] for r in self.results if r['response_time_ms'] > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        median_response_time = statistics.median(response_times) if response_times else 0

        # Additional statistics for large-scale testing
        std_dev_response_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
        percentile_95 = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max_response_time
        percentile_99 = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max_response_time

        # Throughput calculations
        if self.results:
            start_time = min([datetime.fromisoformat(r['timestamp']) for r in self.results])
            end_time = max([datetime.fromisoformat(r['timestamp']) for r in self.results])
            total_duration = (end_time - start_time).total_seconds()
            requests_per_second = len(self.results) / total_duration if total_duration > 0 else 0
        else:
            total_duration = 0
            requests_per_second = 0

        # Endpoint statistics
        endpoint_stats = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'avg_response_time': 0,
                    'response_times': []
                }

            endpoint_stats[endpoint]['total_requests'] += 1
            endpoint_stats[endpoint]['response_times'].append(result['response_time_ms'])

            if result['success']:
                endpoint_stats[endpoint]['successful_requests'] += 1
            else:
                endpoint_stats[endpoint]['failed_requests'] += 1

        # Calculate averages for each endpoint
        for endpoint, stats in endpoint_stats.items():
            if stats['response_times']:
                stats['avg_response_time'] = round(statistics.mean(stats['response_times']), 2)
                stats['success_rate'] = round((stats['successful_requests'] / stats['total_requests']) * 100, 2)
            del stats['response_times']  # Remove raw data for cleaner output

        # Error analysis
        errors = [r for r in self.results if not r['success'] and r['error']]
        error_summary = {}
        for error in errors:
            error_msg = error['error']
            if error_msg not in error_summary:
                error_summary[error_msg] = 0
            error_summary[error_msg] += 1

        # File size analysis (for conversion tests)
        conversion_results = [r for r in self.results if r['endpoint'] == '/convert' and r['success']]
        pdf_sizes = [r['response_size_bytes'] for r in conversion_results if r['response_size_bytes'] > 0]
        html_sizes = [r.get('html_size', 0) for r in conversion_results if r.get('html_size', 0) > 0]

        analytics = {
            'test_summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate_percent': round(success_rate, 2),
                'test_duration': f"{max([datetime.fromisoformat(r['timestamp']) for r in self.results]) - min([datetime.fromisoformat(r['timestamp']) for r in self.results])}"
            },
            'performance_metrics': {
                'avg_response_time_ms': round(avg_response_time, 2),
                'min_response_time_ms': round(min_response_time, 2),
                'max_response_time_ms': round(max_response_time, 2),
                'median_response_time_ms': round(median_response_time, 2),
                'std_dev_response_time_ms': round(std_dev_response_time, 2),
                'percentile_95_ms': round(percentile_95, 2),
                'percentile_99_ms': round(percentile_99, 2),
                'total_duration_seconds': round(total_duration, 2),
                'requests_per_second': round(requests_per_second, 2)
            },
            'endpoint_analysis': endpoint_stats,
            'error_analysis': error_summary,
            'file_size_analysis': {
                'pdf_files_generated': len(pdf_sizes),
                'avg_pdf_size_bytes': round(statistics.mean(pdf_sizes), 2) if pdf_sizes else 0,
                'avg_pdf_size_kb': round(statistics.mean(pdf_sizes) / 1024, 2) if pdf_sizes else 0,
                'avg_html_size_bytes': round(statistics.mean(html_sizes), 2) if html_sizes else 0,
                'avg_html_size_kb': round(statistics.mean(html_sizes) / 1024, 2) if html_sizes else 0,
                'compression_ratio': round(statistics.mean(pdf_sizes) / statistics.mean(html_sizes), 2) if pdf_sizes and html_sizes else 0
            },
            'detailed_results': self.results
        }

        return analytics

    def print_analytics(self):
        """Print formatted analytics report"""
        analytics = self.generate_analytics()

        print("\n" + "=" * 80)
        print("📊 TEST ANALYTICS REPORT")
        print("=" * 80)

        # Test Summary
        summary = analytics['test_summary']
        print(f"\n📋 TEST SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Successful: {summary['successful_tests']} ✅")
        print(f"   Failed: {summary['failed_tests']} ❌")
        print(f"   Success Rate: {summary['success_rate_percent']}%")
        print(f"   Duration: {summary['test_duration']}")

        # Performance Metrics
        perf = analytics['performance_metrics']
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   Average Response Time: {perf['avg_response_time_ms']}ms")
        print(f"   Fastest Response: {perf['min_response_time_ms']}ms")
        print(f"   Slowest Response: {perf['max_response_time_ms']}ms")
        print(f"   Median Response Time: {perf['median_response_time_ms']}ms")
        print(f"   Standard Deviation: {perf['std_dev_response_time_ms']}ms")
        print(f"   95th Percentile: {perf['percentile_95_ms']}ms")
        print(f"   99th Percentile: {perf['percentile_99_ms']}ms")

        print(f"\n🚀 THROUGHPUT METRICS:")
        print(f"   Total Duration: {perf['total_duration_seconds']}s")
        print(f"   Requests per Second: {perf['requests_per_second']}")

        # Endpoint Analysis
        print(f"\n🎯 ENDPOINT ANALYSIS:")
        for endpoint, stats in analytics['endpoint_analysis'].items():
            print(f"   {endpoint}:")
            print(f"     Requests: {stats['total_requests']}")
            print(f"     Success Rate: {stats['success_rate']}%")
            print(f"     Avg Response Time: {stats['avg_response_time']}ms")
        

        # File Size Analysis
        file_analysis = analytics['file_size_analysis']
        if file_analysis['pdf_files_generated'] > 0:
            print(f"\n📄 FILE SIZE ANALYSIS:")
            print(f"   PDFs Generated: {file_analysis['pdf_files_generated']}")
            print(f"   Avg PDF Size: {file_analysis['avg_pdf_size_kb']} KB")
            print(f"   Avg HTML Size: {file_analysis['avg_html_size_kb']} KB")
            print(f"   Compression Ratio: {file_analysis['compression_ratio']}x")

        print("\n" + "=" * 80)

    def save_analytics_json(self, filename: str = None):
        """Save analytics to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_analytics_{timestamp}.json"

        analytics = self.generate_analytics()

        with open(filename, 'w') as f:
            json.dump(analytics, f, indent=2, default=str)

        print(f"📁 Analytics saved to: {filename}")
        return filename


def run_large_scale_test(base_url: str = "http://localhost:5000", num_requests: int = 100):
    """Run large-scale test with many requests"""
    print(f"🏃‍♂️ Running Large-Scale Raw HTML Test ({num_requests} requests)...")

    tester = APITester(base_url)
    tester.run_raw_html_test(num_requests)

    # Print analytics
    tester.print_analytics()

    return tester


def test_custom_html(base_url: str = "http://localhost:5000", html_content: str = None):
    """Test with custom HTML content"""
    if html_content is None:
        print("Please provide HTML content to test")
        return

    print("🧪 Testing Custom HTML...")
    tester = APITester(base_url)

    payload = {"html": html_content}

    start_time = time.time()
    try:
        response = tester.session.post(
            f"{base_url}/convert",
            json=payload,
            timeout=30
        )
        response_time = time.time() - start_time

        success = response.status_code == 200 and response.headers.get('content-type') == 'application/pdf'

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time*1000:.2f}ms")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Response Size: {len(response.content)} bytes")
        print(f"Success: {'✅' if success else '❌'}")

        if success:
            # Save PDF for inspection
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"test_output_{timestamp}.pdf"
            with open(pdf_filename, 'wb') as f:
                f.write(response.content)
            print(f"📄 PDF saved as: {pdf_filename}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Raw HTML Conversion Testing Tool with Analytics')
    parser.add_argument('--url', default='http://localhost:5000',
                       help='Base URL of the API (default: http://localhost:5000)')
    parser.add_argument('--requests', type=int, default=100, metavar='N',
                       help='Number of requests to send (default: 100)')
    parser.add_argument('--save-json', action='store_true',
                       help='Save analytics to JSON file')
    parser.add_argument('--html-file', type=str,
                       help='Test with HTML content from file')

    args = parser.parse_args()

    # Custom HTML test mode
    if args.html_file:
        if os.path.exists(args.html_file):
            with open(args.html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            test_custom_html(args.url, html_content)
        else:
            print(f"❌ File not found: {args.html_file}")
        return

    # Large-scale raw HTML test mode (default)
    tester = run_large_scale_test(args.url, args.requests)

    if args.save_json:
        tester.save_analytics_json()


if __name__ == "__main__":
    main()
