# Concurrent API Testing Tool

A specialized testing tool that launches multiple requests **simultaneously** to test how your HTML to PDF API handles concurrent load.

## 🎯 What This Tests

Unlike the sequential testing tool (`test_api.py`), this tool:
- **Launches all requests at the same time** using threading
- **Tests concurrent load handling** capabilities
- **Measures concurrency efficiency** and resource utilization
- **Identifies bottlenecks** under simultaneous load
- **Analyzes response time variance** under concurrent stress

## 🚀 Usage

### Basic Concurrent Test (20 simultaneous requests)
```bash
python concurrent_test.py
```

### Custom Number of Concurrent Requests
```bash
python concurrent_test.py --concurrent 50
```

### Test Different Server
```bash
python concurrent_test.py --url http://your-server:5000 --concurrent 30
```

### Save Analytics to JSON
```bash
python concurrent_test.py --concurrent 25 --save-json
```

## 📊 Analytics Provided

### Concurrent Test Summary
- Total simultaneous requests launched
- Success/failure rates under concurrent load
- Total execution time for all concurrent requests
- **Concurrency efficiency** (speedup factor)

### Response Time Metrics
- Average, min, max, median response times
- Standard deviation (consistency under load)
- 95th and 99th percentiles
- Response time variance analysis

### Concurrency Analysis
- **Actual vs theoretical execution time**
- **Concurrency speedup factor** (how much faster than sequential)
- **Effective requests per second** under concurrent load
- **Resource utilization efficiency**

### Performance Insights
- Automatic analysis of concurrent performance
- Bottleneck identification
- Load handling assessment

## 📈 Sample Output

```
🏃‍♂️ Running Concurrent Load Test (20 simultaneous requests)...
🚀 Starting Concurrent Raw HTML Test...
📍 Target URL: http://localhost:5000
🔢 Concurrent requests: 20
⏰ Start time: 2024-01-15 14:30:25
======================================================================

✅ PASS [T1] | Concurrent Raw HTML #1 | 200 | 324.56ms
✅ PASS [T3] | Concurrent Raw HTML #3 | 200 | 298.23ms
✅ PASS [T2] | Concurrent Raw HTML #2 | 200 | 312.45ms
✅ PASS [T5] | Concurrent Raw HTML #5 | 200 | 287.89ms
...

======================================================================
✅ All 20 concurrent requests completed!
⏱️  Total execution time: 2.45 seconds
🚀 Average requests per second: 8.16

📊 CONCURRENT TEST ANALYTICS REPORT
================================================================================

📋 CONCURRENT TEST SUMMARY:
   Total Requests: 20
   Successful: 19 ✅
   Failed: 1 ❌
   Success Rate: 95.00%
   Total Duration: 2.45s
   Concurrency Efficiency: 2.45x

⚡ RESPONSE TIME METRICS:
   Average Response Time: 298.45ms
   Fastest Response: 156.23ms
   Slowest Response: 445.67ms
   Median Response Time: 287.34ms
   Standard Deviation: 89.12ms
   95th Percentile: 398.78ms
   99th Percentile: 445.67ms

🚀 CONCURRENCY ANALYSIS:
   Requests Launched: 20
   Actual Execution Time: 2.45s
   Avg Individual Request Time: 0.30s
   Theoretical Sequential Time: 6.00s
   Concurrency Speedup: 2.45x
   Effective RPS: 8.16

💡 PERFORMANCE INSIGHTS:
   ✅ Excellent success rate under concurrent load
   ✅ Consistent response times across concurrent requests
   ✅ Good concurrency handling and resource utilization
```

## 🔍 Key Differences from Sequential Testing

| Aspect | Sequential (`test_api.py`) | Concurrent (`concurrent_test.py`) |
|--------|---------------------------|-----------------------------------|
| **Execution** | One request at a time | All requests simultaneously |
| **Purpose** | Volume testing | Load testing |
| **Metrics** | Throughput over time | Concurrency efficiency |
| **Bottlenecks** | API processing speed | Resource contention |
| **Use Case** | High-volume scenarios | Peak load scenarios |

## 🎯 When to Use Each Tool

### Use `test_api.py` (Sequential) when:
- Testing **high-volume** processing (hundreds/thousands of requests)
- Measuring **sustained throughput**
- Testing **API stability** over time
- Analyzing **individual request performance**

### Use `concurrent_test.py` (Concurrent) when:
- Testing **peak load** scenarios
- Measuring **concurrent user** handling
- Identifying **resource bottlenecks**
- Testing **thread safety** and **race conditions**
- Simulating **real-world traffic spikes**

## 🔧 Technical Details

- Uses `ThreadPoolExecutor` for true concurrent execution
- Thread-safe result logging with locks
- Unique HTML content per request (with request ID and timestamp)
- Individual sessions per thread to avoid connection sharing
- Extended timeouts for concurrent scenarios

## 📁 Files Generated

- `concurrent_test_analytics_YYYYMMDD_HHMMSS.json`: Detailed concurrent analytics
- Real-time console output with thread identification

## 💡 Performance Tips

1. **Start small**: Begin with 10-20 concurrent requests
2. **Monitor resources**: Watch CPU and memory usage during tests
3. **Adjust timeouts**: Increase timeout values for high concurrency
4. **Compare results**: Run both sequential and concurrent tests for complete analysis

## 🚨 Important Notes

- Concurrent testing puts **higher load** on your server
- Monitor your server resources during testing
- Some failures under high concurrency are normal
- Results help identify optimal concurrent user limits
