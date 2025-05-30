#!/usr/bin/env python3
"""
Concurrent API Testing Script for HTML to PDF Converter

This script tests the Flask API by launching multiple requests simultaneously
to test concurrent load handling and provides detailed analytics.
"""

import requests
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
import os
import threading
import concurrent.futures
from queue import Queue


class ConcurrentAPITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.results_lock = threading.Lock()

    def log_result(self, test_name: str, method: str, endpoint: str,
                   status_code: int, response_time: float,
                   success: bool, error: str = None,
                   response_size: int = 0, thread_id: int = None, **kwargs):
        """Thread-safe logging of test results"""
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
            'thread_id': thread_id,
            **kwargs
        }

        with self.results_lock:
            self.results.append(result)

        # Print real-time result
        status = "✅ PASS" if success else "❌ FAIL"
        thread_info = f"[T{thread_id}]" if thread_id else ""
        print(f"{status} {thread_info} | {test_name} | {status_code} | {result['response_time_ms']}ms")
        if error:
            print(f"    Error: {error}")

    def single_raw_html_request(self, request_id: int):
        """Execute a single raw HTML conversion request"""
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Concurrent Test #{request_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .request-info {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Concurrent Raw HTML Test</h1>
    <div class="request-info">
        <p><strong>Request ID:</strong> {request_id}</p>
        <p><strong>Timestamp:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}</p>
        <p><strong>Thread:</strong> {threading.current_thread().name}</p>
    </div>
    <p>This HTML was sent as raw body content in a concurrent test scenario.</p>
    <p>Testing concurrent load handling capabilities of the API.</p>
</body>
</html>"""

        session = requests.Session()
        start_time = time.time()

        try:
            response = session.post(
                f"{self.base_url}/convert",
                data=html_content,
                headers={'Content-Type': 'text/html'},
                timeout=60  # Longer timeout for concurrent requests
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
                test_name=f"Concurrent Raw HTML #{request_id}",
                method="POST",
                endpoint="/convert",
                status_code=response.status_code,
                response_time=response_time,
                success=success,
                error=error,
                response_size=len(response.content),
                content_type=response.headers.get('content-type'),
                html_size=len(html_content),
                thread_id=request_id,
                request_id=request_id
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name=f"Concurrent Raw HTML #{request_id}",
                method="POST",
                endpoint="/convert",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e),
                thread_id=request_id,
                request_id=request_id
            )
        finally:
            session.close()

    def run_concurrent_test(self, num_concurrent: int = 20):
        """Run concurrent requests using ThreadPoolExecutor"""
        print(f"🚀 Starting Concurrent Raw HTML Test...")
        print(f"📍 Target URL: {self.base_url}")
        print(f"🔢 Concurrent requests: {num_concurrent}")
        print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        start_time = time.time()

        # Use ThreadPoolExecutor for concurrent execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            # Submit all requests
            futures = [executor.submit(self.single_raw_html_request, i+1) for i in range(num_concurrent)]

            # Wait for all requests to complete
            concurrent.futures.wait(futures)

        total_time = time.time() - start_time

        print("\n" + "=" * 70)
        print(f"✅ All {num_concurrent} concurrent requests completed!")
        print(f"⏱️  Total execution time: {total_time:.2f} seconds")
        print(f"🚀 Average requests per second: {num_concurrent / total_time:.2f}")

    def generate_concurrent_analytics(self) -> Dict[str, Any]:
        """Generate analytics specifically for concurrent testing"""
        if not self.results:
            return {"error": "No test results available"}

        # Basic statistics
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100

        # Response time statistics
        response_times = [r['response_time_ms'] for r in self.results if r['response_time_ms'] > 0]

        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
            std_dev_response_time = statistics.stdev(response_times) if len(response_times) > 1 else 0

            # Percentiles for concurrent load analysis
            percentile_95 = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max_response_time
            percentile_99 = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = median_response_time = 0
            std_dev_response_time = percentile_95 = percentile_99 = 0

        # Concurrent execution analysis
        if self.results:
            timestamps = [datetime.fromisoformat(r['timestamp']) for r in self.results]
            start_time = min(timestamps)
            end_time = max(timestamps)
            total_duration = (end_time - start_time).total_seconds()

            # Calculate actual concurrency
            successful_times = [r['response_time_ms'] for r in self.results if r['success']]
            avg_execution_time = statistics.mean(successful_times) / 1000 if successful_times else 0
            theoretical_sequential_time = avg_execution_time * total_requests
            concurrency_efficiency = (theoretical_sequential_time / total_duration) if total_duration > 0 else 0
        else:
            total_duration = 0
            concurrency_efficiency = 0

        # Error analysis
        errors = [r for r in self.results if not r['success'] and r['error']]
        error_summary = {}
        for error in errors:
            error_msg = error['error']
            if error_msg not in error_summary:
                error_summary[error_msg] = 0
            error_summary[error_msg] += 1

        # File size analysis
        pdf_sizes = [r['response_size_bytes'] for r in self.results if r['success'] and r['response_size_bytes'] > 0]
        html_sizes = [r.get('html_size', 0) for r in self.results if r.get('html_size', 0) > 0]

        analytics = {
            'concurrent_test_summary': {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'failed_requests': failed_requests,
                'success_rate_percent': round(success_rate, 2),
                'total_duration_seconds': round(total_duration, 2),
                'concurrency_efficiency': round(concurrency_efficiency, 2)
            },
            'performance_metrics': {
                'avg_response_time_ms': round(avg_response_time, 2),
                'min_response_time_ms': round(min_response_time, 2),
                'max_response_time_ms': round(max_response_time, 2),
                'median_response_time_ms': round(median_response_time, 2),
                'std_dev_response_time_ms': round(std_dev_response_time, 2),
                'percentile_95_ms': round(percentile_95, 2),
                'percentile_99_ms': round(percentile_99, 2)
            },
            'concurrency_analysis': {
                'requests_launched_simultaneously': total_requests,
                'actual_execution_time_seconds': round(total_duration, 2),
                'average_individual_request_time_seconds': round(avg_execution_time, 2),
                'theoretical_sequential_time_seconds': round(theoretical_sequential_time, 2),
                'concurrency_speedup_factor': round(concurrency_efficiency, 2),
                'effective_requests_per_second': round(total_requests / total_duration, 2) if total_duration > 0 else 0
            },
            'error_analysis': error_summary,
            'file_size_analysis': {
                'pdf_files_generated': len(pdf_sizes),
                'avg_pdf_size_bytes': round(statistics.mean(pdf_sizes), 2) if pdf_sizes else 0,
                'avg_pdf_size_kb': round(statistics.mean(pdf_sizes) / 1024, 2) if pdf_sizes else 0,
                'total_data_transferred_mb': round(sum(pdf_sizes) / (1024 * 1024), 2) if pdf_sizes else 0
            },
            'detailed_results': self.results
        }

        return analytics

    def print_concurrent_analytics(self):
        """Print formatted analytics report for concurrent testing"""
        analytics = self.generate_concurrent_analytics()

        print("\n" + "=" * 80)
        print("📊 CONCURRENT TEST ANALYTICS REPORT")
        print("=" * 80)

        # Test Summary
        summary = analytics['concurrent_test_summary']
        print(f"\n📋 CONCURRENT TEST SUMMARY:")
        print(f"   Total Requests: {summary['total_requests']}")
        print(f"   Successful: {summary['successful_requests']} ✅")
        print(f"   Failed: {summary['failed_requests']} ❌")
        print(f"   Success Rate: {summary['success_rate_percent']}%")
        print(f"   Total Duration: {summary['total_duration_seconds']}s")
        print(f"   Concurrency Efficiency: {summary['concurrency_efficiency']}x")

        # Performance Metrics
        perf = analytics['performance_metrics']
        print(f"\n⚡ RESPONSE TIME METRICS:")
        print(f"   Average Response Time: {perf['avg_response_time_ms']}ms")
        print(f"   Fastest Response: {perf['min_response_time_ms']}ms")
        print(f"   Slowest Response: {perf['max_response_time_ms']}ms")
        print(f"   Median Response Time: {perf['median_response_time_ms']}ms")
        print(f"   Standard Deviation: {perf['std_dev_response_time_ms']}ms")
        print(f"   95th Percentile: {perf['percentile_95_ms']}ms")
        print(f"   99th Percentile: {perf['percentile_99_ms']}ms")

        # Concurrency Analysis
        conc = analytics['concurrency_analysis']
        print(f"\n🚀 CONCURRENCY ANALYSIS:")
        print(f"   Requests Launched: {conc['requests_launched_simultaneously']}")
        print(f"   Actual Execution Time: {conc['actual_execution_time_seconds']}s")
        print(f"   Avg Individual Request Time: {conc['average_individual_request_time_seconds']}s")
        print(f"   Theoretical Sequential Time: {conc['theoretical_sequential_time_seconds']}s")
        print(f"   Concurrency Speedup: {conc['concurrency_speedup_factor']}x")
        print(f"   Effective RPS: {conc['effective_requests_per_second']}")

        # Error Analysis
        if analytics['error_analysis']:
            print(f"\n🚨 ERROR ANALYSIS:")
            for error, count in analytics['error_analysis'].items():
                print(f"   {error}: {count} occurrences")

        # File Size Analysis
        file_analysis = analytics['file_size_analysis']
        if file_analysis['pdf_files_generated'] > 0:
            print(f"\n📄 FILE SIZE ANALYSIS:")
            print(f"   PDFs Generated: {file_analysis['pdf_files_generated']}")
            print(f"   Avg PDF Size: {file_analysis['avg_pdf_size_kb']} KB")
            print(f"   Total Data Transferred: {file_analysis['total_data_transferred_mb']} MB")

        print("\n" + "=" * 80)

        # Performance insights
        print("\n💡 PERFORMANCE INSIGHTS:")
        if summary['success_rate_percent'] >= 95:
            print("   ✅ Excellent success rate under concurrent load")
        elif summary['success_rate_percent'] >= 80:
            print("   ⚠️  Good success rate, some requests failed under load")
        else:
            print("   ❌ Poor success rate, API struggling with concurrent load")

        if perf['std_dev_response_time_ms'] < perf['avg_response_time_ms'] * 0.3:
            print("   ✅ Consistent response times across concurrent requests")
        else:
            print("   ⚠️  High variance in response times under concurrent load")

        if conc['concurrency_speedup_factor'] > 0.7:
            print("   ✅ Good concurrency handling and resource utilization")
        else:
            print("   ⚠️  Limited concurrency benefits, possible bottlenecks")

    def save_concurrent_analytics_json(self, filename: str = None):
        """Save concurrent analytics to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"concurrent_test_analytics_{timestamp}.json"

        analytics = self.generate_concurrent_analytics()

        with open(filename, 'w') as f:
            json.dump(analytics, f, indent=2, default=str)

        print(f"📁 Concurrent analytics saved to: {filename}")
        return filename


def run_concurrent_load_test(base_url: str = "http://localhost:5000", num_concurrent: int = 20):
    """Run concurrent load test"""
    print(f"🏃‍♂️ Running Concurrent Load Test ({num_concurrent} simultaneous requests)...")

    tester = ConcurrentAPITester(base_url)
    tester.run_concurrent_test(num_concurrent)

    # Print analytics
    tester.print_concurrent_analytics()

    return tester


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Concurrent Raw HTML Conversion Testing Tool')
    parser.add_argument('--url', default='http://localhost:5000',
                       help='Base URL of the API (default: http://localhost:5000)')
    parser.add_argument('--concurrent', type=int, default=20, metavar='N',
                       help='Number of concurrent requests (default: 20)')
    parser.add_argument('--save-json', action='store_true',
                       help='Save analytics to JSON file')

    args = parser.parse_args()

    # Run concurrent test
    tester = run_concurrent_load_test(args.url, args.concurrent)

    if args.save_json:
        tester.save_concurrent_analytics_json()


if __name__ == "__main__":
    main()
