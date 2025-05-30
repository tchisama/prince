#!/usr/bin/env python3
"""
Concurrent Invoice Generation Testing Script for HTML to PDF Converter

This script tests the Flask API by generating professional invoices with random data
and launching multiple requests simultaneously to test concurrent load handling.
Generated PDFs are saved to ./tmp folder and detailed analytics are provided.
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
import random
import string


class ConcurrentAPITester:
    def __init__(self, base_url: str = "http://localhost:5000", save_pdfs: bool = True):
        self.base_url = base_url
        self.results = []
        self.results_lock = threading.Lock()
        self.save_pdfs = save_pdfs
        self.tmp_folder = "./tmp"

        # Create tmp folder if it doesn't exist
        if self.save_pdfs and not os.path.exists(self.tmp_folder):
            os.makedirs(self.tmp_folder)
            print(f"📁 Created {self.tmp_folder} folder for saving PDFs")

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

    def generate_random_invoice_data(self, request_id: int) -> dict:
        """Generate random invoice data for testing"""
        companies = [
            "TechCorp Solutions", "Global Dynamics Inc", "Innovation Labs LLC",
            "Digital Ventures Co", "Future Systems Ltd", "Alpha Technologies",
            "Beta Enterprises", "Gamma Industries", "Delta Corporation", "Epsilon Group"
        ]

        products = [
            ("Web Development Service", 150.00, 250.00),
            ("Software Consulting", 200.00, 400.00),
            ("Database Design", 100.00, 180.00),
            ("API Integration", 80.00, 150.00),
            ("Mobile App Development", 300.00, 500.00),
            ("Cloud Migration", 250.00, 450.00),
            ("Security Audit", 180.00, 320.00),
            ("Performance Optimization", 120.00, 220.00),
            ("Technical Documentation", 60.00, 120.00),
            ("Training Session", 90.00, 160.00)
        ]

        # Generate random invoice data
        invoice_data = {
            'invoice_number': f"INV-{random.randint(10000, 99999)}",
            'date': datetime.now().strftime("%Y-%m-%d"),
            'due_date': (datetime.now().replace(day=28) if datetime.now().day < 28 else
                        datetime.now().replace(month=datetime.now().month+1, day=28)).strftime("%Y-%m-%d"),
            'company_name': random.choice(companies),
            'client_name': f"{random.choice(['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Tom', 'Emma'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'])}",
            'client_email': f"{''.join(random.choices(string.ascii_lowercase, k=8))}@{''.join(random.choices(string.ascii_lowercase, k=6))}.com",
            'client_address': f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Cedar', 'Maple'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr', 'Ln'])}",
            'client_city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego']),
            'client_zip': f"{random.randint(10000, 99999)}",
            'items': [],
            'request_id': request_id
        }

        # Generate 2-5 random items
        num_items = random.randint(2, 5)
        total = 0

        for i in range(num_items):
            product_name, min_price, max_price = random.choice(products)
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(min_price, max_price), 2)
            line_total = quantity * unit_price
            total += line_total

            invoice_data['items'].append({
                'description': product_name,
                'quantity': quantity,
                'unit_price': unit_price,
                'total': line_total
            })

        # Calculate tax and final total
        tax_rate = 0.08  # 8% tax
        subtotal = total
        tax_amount = round(subtotal * tax_rate, 2)
        final_total = subtotal + tax_amount

        invoice_data.update({
            'subtotal': subtotal,
            'tax_rate': tax_rate * 100,
            'tax_amount': tax_amount,
            'total': final_total
        })

        return invoice_data

    def single_raw_html_request(self, request_id: int):
        """Execute a single raw HTML conversion request"""
        # Generate random invoice data
        invoice = self.generate_random_invoice_data(request_id)

        # Generate professional invoice HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Invoice {invoice['invoice_number']}</title>
    <meta charset="UTF-8">
    <style>
        document {{
            padding: 0;
            margin: 0;
        }}
        html{{
            padding: 0;
            margin: 0;
        }}
        @page {{
            size: A4;
            padding:0;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background: #fff;
        }}

        .invoice-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }}

        .invoice-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .invoice-title {{
            font-size: 2.5em;
            font-weight: 300;
            margin: 0;
            letter-spacing: 2px;
        }}

        .invoice-number {{
            font-size: 1.2em;
            margin-top: 10px;
            opacity: 0.9;
        }}

        .invoice-body {{
            padding: 40px;
        }}

        .company-info {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}

        .company-name {{
            font-size: 1.8em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .invoice-details {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }}

        .bill-to, .invoice-info {{
            flex: 1;
            min-width: 250px;
            margin-bottom: 20px;
        }}

        .bill-to {{
            margin-right: 40px;
        }}

        .section-title {{
            font-size: 1.1em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .client-info {{
            background: #f8f9ff;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .client-name {{
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 5px;
        }}

        .invoice-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}

        .invoice-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9em;
        }}

        .invoice-table td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}

        .invoice-table tr:nth-child(even) {{
            background: #f8f9ff;
        }}

        .invoice-table tr:hover {{
            background: #f0f2ff;
        }}

        .text-right {{
            text-align: right;
        }}

        .text-center {{
            text-align: center;
        }}

        .totals-section {{
            margin-top: 30px;
            display: flex;
            justify-content: flex-end;
        }}

        .totals-table {{
            width: 300px;
            border-collapse: collapse;
        }}

        .totals-table td {{
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }}

        .totals-table .total-row {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            font-size: 1.1em;
        }}

        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #eee;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}

        .test-info {{
            margin-top: 40px;
            padding: 20px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            font-size: 0.9em;
        }}

        .test-info h4 {{
            margin: 0 0 10px 0;
            color: #856404;
        }}

        @media print {{
            .test-info {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="invoice-container">
        <div class="invoice-header">
            <h1 class="invoice-title">INVOICE</h1>
            <div class="invoice-number">{invoice['invoice_number']}</div>
        </div>

        <div class="invoice-body">
            <div class="company-info">
                <div class="company-name">{invoice['company_name']}</div>
                <div>Professional Services & Solutions</div>
            </div>

            <div class="invoice-details">
                <div class="bill-to">
                    <div class="section-title">Bill To</div>
                    <div class="client-info">
                        <div class="client-name">{invoice['client_name']}</div>
                        <div>{invoice['client_email']}</div>
                        <div>{invoice['client_address']}</div>
                        <div>{invoice['client_city']}, {invoice['client_zip']}</div>
                    </div>
                </div>

                <div class="invoice-info">
                    <div class="section-title">Invoice Details</div>
                    <table style="width: 100%;">
                        <tr>
                            <td><strong>Invoice Date:</strong></td>
                            <td>{invoice['date']}</td>
                        </tr>
                        <tr>
                            <td><strong>Due Date:</strong></td>
                            <td>{invoice['due_date']}</td>
                        </tr>
                        <tr>
                            <td><strong>Request ID:</strong></td>
                            <td>#{invoice['request_id']}</td>
                        </tr>
                    </table>
                </div>
            </div>

            <table class="invoice-table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th class="text-center">Quantity</th>
                        <th class="text-right">Unit Price</th>
                        <th class="text-right">Total</th>
                    </tr>
                </thead>
                <tbody>"""

        # Add invoice items
        for item in invoice['items']:
            html_content += f"""
                    <tr>
                        <td>{item['description']}</td>
                        <td class="text-center">{item['quantity']}</td>
                        <td class="text-right">${item['unit_price']:.2f}</td>
                        <td class="text-right">${item['total']:.2f}</td>
                    </tr>"""

        html_content += f"""
                </tbody>
            </table>

            <div class="totals-section">
                <table class="totals-table">
                    <tr>
                        <td><strong>Subtotal:</strong></td>
                        <td class="text-right">${invoice['subtotal']:.2f}</td>
                    </tr>
                    <tr>
                        <td><strong>Tax ({invoice['tax_rate']:.0f}%):</strong></td>
                        <td class="text-right">${invoice['tax_amount']:.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td><strong>TOTAL:</strong></td>
                        <td class="text-right"><strong>${invoice['total']:.2f}</strong></td>
                    </tr>
                </table>
            </div>

            <div class="footer">
                <p>Thank you for your business!</p>
                <p>Payment is due within 30 days of invoice date.</p>
            </div>

            <div class="test-info">
                <h4>🧪 Concurrent Test Information</h4>
                <p><strong>Request ID:</strong> {request_id}</p>
                <p><strong>Timestamp:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}</p>
                <p><strong>Thread:</strong> {threading.current_thread().name}</p>
                <p>This invoice was generated as part of a concurrent API load test.</p>
            </div>
        </div>
    </div>
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
            pdf_filename = None

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
            else:
                # Save PDF if successful and save_pdfs is enabled
                if self.save_pdfs:
                    pdf_filename = f"invoice_{invoice['invoice_number']}_req{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    pdf_path = os.path.join(self.tmp_folder, pdf_filename)

                    try:
                        with open(pdf_path, 'wb') as f:
                            f.write(response.content)
                        print(f"💾 Saved PDF: {pdf_filename}")
                    except Exception as save_error:
                        error = f"Failed to save PDF: {str(save_error)}"
                        success = False

            self.log_result(
                test_name=f"Invoice Generation #{request_id}",
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
                request_id=request_id,
                invoice_number=invoice['invoice_number'],
                pdf_filename=pdf_filename,
                invoice_total=invoice['total']
            )

        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(
                test_name=f"Invoice Generation #{request_id}",
                method="POST",
                endpoint="/convert",
                status_code=0,
                response_time=response_time,
                success=False,
                error=str(e),
                thread_id=request_id,
                request_id=request_id,
                invoice_number="ERROR",
                pdf_filename=None,
                invoice_total=0
            )
        finally:
            session.close()

    def run_concurrent_test(self, num_concurrent: int = 20):
        """Run concurrent requests using ThreadPoolExecutor"""
        print(f"🚀 Starting Concurrent Invoice Generation Test...")
        print(f"📍 Target URL: {self.base_url}")
        print(f"🔢 Concurrent requests: {num_concurrent}")
        print(f"💾 Save PDFs: {'Yes' if self.save_pdfs else 'No'}")
        if self.save_pdfs:
            print(f"📁 Save folder: {self.tmp_folder}")
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
        print(f"✅ All {num_concurrent} concurrent invoice generation requests completed!")
        print(f"⏱️  Total execution time: {total_time:.2f} seconds")
        print(f"🚀 Average requests per second: {num_concurrent / total_time:.2f}")
        if self.save_pdfs:
            successful_pdfs = sum(1 for r in self.results if r.get('success', False) and r.get('pdf_filename'))
            print(f"💾 PDFs saved: {successful_pdfs}/{num_concurrent}")
            print(f"📁 Check {self.tmp_folder} folder for generated invoices")

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


def run_concurrent_load_test(base_url: str = "http://localhost:5000", num_concurrent: int = 20, save_pdfs: bool = True):
    """Run concurrent load test"""
    print(f"🏃‍♂️ Running Concurrent Invoice Generation Test ({num_concurrent} simultaneous requests)...")

    tester = ConcurrentAPITester(base_url, save_pdfs)
    tester.run_concurrent_test(num_concurrent)

    # Print analytics
    tester.print_concurrent_analytics()

    return tester


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Concurrent Invoice Generation Testing Tool')
    parser.add_argument('--url', default='http://localhost:5000',
                       help='Base URL of the API (default: http://localhost:5000)')
    parser.add_argument('--concurrent', type=int, default=20, metavar='N',
                       help='Number of concurrent requests (default: 20)')
    parser.add_argument('--save-json', action='store_true',
                       help='Save analytics to JSON file')
    parser.add_argument('--no-save-pdfs', action='store_true',
                       help='Disable saving PDFs to ./tmp folder')

    args = parser.parse_args()

    # Run concurrent test
    save_pdfs = not args.no_save_pdfs
    tester = run_concurrent_load_test(args.url, args.concurrent, save_pdfs)

    if args.save_json:
        tester.save_concurrent_analytics_json()


if __name__ == "__main__":
    main()
