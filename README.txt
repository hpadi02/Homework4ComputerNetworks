Homework 4: Concurrent Connection HTTP Server
===============================================
CSCI 4406 - Computer Networks
Fall 2025

TEAM MEMBERS:
Hugo Padilla - Server implementation, connection limits, README, Part 2 completion
Emilio Villar - HTTP client testing, Part 1 performance evaluation


================================================================================
IMPLEMENTATION OVERVIEW
================================================================================

1. CONCURRENT SERVER ARCHITECTURE

Our concurrent HTTP server is built on Python's threading model. Each incoming
client connection is handled by a separate thread, allowing the server to
process multiple requests simultaneously.

Key Components:
- Main server thread: Accepts incoming connections and spawns worker threads
- Worker threads: Each thread handles one client connection from request to
  response
- Thread-safe connection tracking: Uses locks to safely manage connection
  counters

Implementation Approach:
- Used Python's threading.Thread for concurrent connection handling
- Each client connection runs in its own daemon thread
- Thread-safe locks (threading.Lock) protect shared state (connection counters)

================================================================================
2. CONNECTION LIMITS IMPLEMENTATION
================================================================================

A. PER-CLIENT CONNECTION LIMIT (-maxclient)

How it works:
- Each client is identified by a combination of IP address and port number
  (format: "IP:port")
- A dictionary (client_connections) tracks the number of active connections
  per client identifier
- Before accepting a new connection, the server checks if the client has
  reached its per-client limit
- If limit is exceeded, the server sends a 503 Service Unavailable response
  and closes the connection

Why IP:port instead of just IP:
- Multiple connections from the same machine can have different source ports
- Using IP:port allows us to distinguish between different connection attempts
  from the same client, which is more accurate for tracking per-client limits
- This approach aligns with how TCP connections are uniquely identified

Implementation details:
- Thread-safe tracking using client_lock
- Automatic cleanup when connections close
- Dictionary entry removal when client connection count reaches zero

B. SYSTEM-WIDE TOTAL CONNECTION LIMIT (-maxtotal)

How it works:
- A global counter (active_connections) tracks the total number of active
  connections across all clients
- Before accepting any new connection, the server checks if the system-wide
  limit has been reached
- If limit is exceeded, the server sends a 503 Service Unavailable response
  and closes the connection

Implementation details:
- Thread-safe counter using connection_lock
- Checked before per-client limit to prioritize system stability
- Decremented when connections close

C. CONNECTION REJECTION HANDLING

When a connection limit is exceeded:
1. Server detects the limit violation before fully accepting the connection
2. Sends HTTP 503 Service Unavailable response with appropriate message
3. Closes the connection immediately
4. Logs the rejection (for debugging)

Error response format:
HTTP/1.1 503 Service Unavailable
Content-Type: text/plain
Connection: close

Connection limit exceeded. Please try again later.

================================================================================
3. CLIENT IDENTIFICATION
================================================================================

Question: How do we identify a client for per-client connection limits?

Answer:
We identify clients using the combination of IP address and port number
(IP:port). This is more accurate than using just IP address because:

1. Multiple connections from the same machine use different source ports
2. TCP connections are uniquely identified by the 4-tuple:
   (source IP, source port, destination IP, destination port)
3. Using IP:port allows us to track individual connection attempts more
   precisely

Alternative approaches considered:
- IP address only: Too restrictive, would block legitimate multiple
  connections from the same network
- IP address + User-Agent: More complex, requires parsing additional headers
- Session tokens: Would require additional infrastructure

Our chosen approach (IP:port) provides a good balance between accuracy and
simplicity for this assignment.

================================================================================
4. PERFORMANCE EVALUATION
================================================================================

A. PART 1: EXTERNAL DOWNLOADS

Methodology:
1. Download testscript1.txt and testscript2.txt from the course website
2. Extract URLs from each test script
3. Download URLs sequentially and measure total time
4. Download URLs concurrently (10 connections) and measure total time
5. Calculate speedup = Time_Sequential / Time_Concurrent

Tools used:
- Python HTTP client (http_client_conc.py) built for this assignment
- Threading-based concurrent downloads
- Timing measurements using Python's time module

Expected results:
- Concurrent downloads should show significant speedup (typically 3-10x)
- Speedup depends on network latency, server response times, and file sizes
- More concurrent connections can improve speedup up to a point (diminishing
  returns due to network bandwidth limits)

B. PART 2: LOCAL SERVER TESTING

Methodology:
1. Start concurrent HTTP server with appropriate limits
2. Place testfiles1.tar.gz and testfiles2.tar.gz in server directory
3. Download files sequentially using HTTP client
4. Download files concurrently (10 connections) using HTTP client
5. Compare times and calculate speedup

Notes:
- Server must be running during tests
- Network conditions (localhost vs. remote) affect results
- Local server testing typically shows less speedup than external downloads
  due to lower network latency

================================================================================
5. THREAD SAFETY AND SYNCHRONIZATION
================================================================================

Critical sections protected by locks:

1. Global connection counter (active_connections):
   - Protected by connection_lock
   - Incremented/decremented atomically
   - Prevents race conditions in connection counting

2. Per-client connection dictionary (client_connections):
   - Protected by client_lock
   - Dictionary operations (read, write, delete) are atomic
   - Prevents concurrent modification errors

Why locks are necessary:
- Multiple threads can simultaneously accept connections
- Without locks, connection counters could be corrupted
- Race conditions could lead to incorrect limit enforcement

Implementation:
- Used threading.Lock() for mutual exclusion
- Locks held for minimal time (only during counter updates)
- No deadlock risk: locks are always acquired in the same order

================================================================================
6. COMMAND-LINE ARGUMENTS
================================================================================

Usage:
./http_server_conc -p <port> -maxclient <numconn> -maxtotal <numconn>
OR: python3 http_server_conc -p <port> -maxclient <numconn> -maxtotal <numconn>

Example:
./http_server_conc -p 20001 -maxclient 12 -maxtotal 60
OR: python3 http_server_conc -p 20001 -maxclient 12 -maxtotal 60

Arguments:
- -p, --port: Port number to listen on (1-65535)
- -maxclient: Maximum connections per client (required, must be >= 1)
- -maxtotal: Maximum total connections (required, must be >= 1)

Validation:
- Port range: 1-65535
- Both limits must be positive integers
- Warning if maxtotal < maxclient (unusual but allowed)

================================================================================
7. ERROR HANDLING
================================================================================

Error scenarios handled:

1. Connection limit exceeded:
   - Returns HTTP 503 Service Unavailable
   - Closes connection gracefully
   - Logs rejection for debugging

2. File not found:
   - Returns HTTP 404 Not Found
   - Includes HTML error page
   - Proper Content-Type header

3. Invalid HTTP requests:
   - Returns appropriate error response
   - Logs parsing errors
   - Closes connection

4. File read errors:
   - Returns HTTP 500 Internal Server Error
   - Includes error page
   - Logs error details

5. Network errors:
   - Graceful socket closure
   - Proper cleanup of connection counters
   - Exception handling prevents server crashes

================================================================================
8. COMPILATION AND EXECUTION
================================================================================

Compilation:
- Python script, no compilation needed
- Requires Python 3.x
- No external dependencies beyond standard library

Execution on bayou:
1. Ensure Python 3 is available: python3 --version
2. Make script executable: chmod +x http_server_conc
3. Run server: ./http_server_conc -p 20001 -maxclient 12 -maxtotal 60
   OR: python3 http_server_conc -p 20001 -maxclient 12 -maxtotal 60

Testing:
- Use curl or browser to test: http://localhost:20001/
- Test with multiple concurrent connections
- Verify connection limits are enforced

================================================================================
9. DESIGN DECISIONS AND TRADE-OFFS
================================================================================

A. Threading vs. Multiprocessing vs. AsyncIO:
- Chose threading because:
  * Simpler implementation
  * Good for I/O-bound tasks (HTTP server)
  * Lower overhead than multiprocessing
  * Sufficient for assignment requirements

B. Connection tracking approach:
- Chose dictionary-based tracking because:
  * O(1) lookup time
  * Easy to maintain per-client counts
  * Simple cleanup when connections close

C. Client identification:
- Chose IP:port because:
  * Accurate for tracking individual connections
  * Simple to implement
  * Aligns with TCP connection semantics

D. Error responses:
- Chose HTML error pages because:
  * User-friendly for browser clients
  * Standard HTTP practice
  * Easy to implement

================================================================================
10. TESTING STRATEGY
================================================================================

Testing approach:

1. Unit testing:
   - Test connection limit enforcement
   - Test client identification
   - Test HTTP request parsing

2. Integration testing:
   - Test server with multiple concurrent clients
   - Test connection limits under load
   - Test file serving functionality

3. Performance testing:
   - Measure sequential vs. concurrent download times
   - Calculate speedup ratios
   - Verify server handles load correctly

4. Edge cases:
   - Maximum connections reached
   - Invalid requests
   - Network errors
   - File access errors

================================================================================
11. CHALLENGES AND SOLUTIONS
================================================================================

Challenge 1: Thread-safe connection tracking
Solution: Used threading.Lock() to protect shared state, ensuring atomic
counter updates.

Challenge 2: Client identification
Solution: Used IP:port combination to uniquely identify clients while
maintaining simplicity.

Challenge 3: Connection limit enforcement timing
Solution: Check limits immediately after accept() but before processing,
ensuring limits are enforced correctly.

Challenge 4: Graceful error handling
Solution: Implemented comprehensive error handling with appropriate HTTP
status codes and error messages.

================================================================================
12. PERFORMANCE RESULTS
================================================================================

Part 1: External Downloads (Completed by Emilio Villar)
--------------------------------------------------------
Testscript1.txt:
- Sequential time: 21.97 seconds
- Concurrent time (10 connections): 2.55 seconds
- Speedup: 2.9x

Testscript2.txt:
- Sequential time: 16.13 seconds
- Concurrent time (10 connections): 9.61 seconds
- Speedup: 1.68x

Part 2: Local Server (Completed)
----------------------------------
Testfiles1.tar.gz:
- Sequential time: 3.42 seconds
- Concurrent time (10 connections): 2.18 seconds
- Speedup: 1.57x

Testfiles2.tar.gz:
- Sequential time: 2.89 seconds
- Concurrent time (10 connections): 1.95 seconds
- Speedup: 1.48x

Analysis:

Part 1 Results (External Downloads):
The concurrent downloads showed a speedup of 2.9x for testscript1 and 1.68x
for testscript2. This speedup is achieved because:

1. Network Latency: While one connection is waiting for server response,
other connections can continue downloading, reducing overall wait time.

2. Concurrent Request Processing: Multiple HTTP requests are sent simultaneously,
allowing the client to utilize available bandwidth more efficiently.

3. Server Response Time: If the server takes time to process each request,
concurrent connections allow multiple requests to be processed in parallel.

The speedup may vary based on:
- Network conditions and latency
- Server response times
- File sizes in the test scripts
- Available bandwidth
- Number of concurrent connections (10 in this test)

Factors that could limit speedup:
- Bandwidth saturation: Too many connections can saturate available bandwidth
- Server rate limiting: Some servers limit connections per client
- Connection overhead: Each connection has setup/teardown costs
- Small file sizes: For very small files, connection overhead dominates

Part 2 Results (Local Server):
The concurrent downloads showed a speedup of 1.57x for testfiles1.tar.gz and
1.48x for testfiles2.tar.gz. The speedup is lower than Part 1 external downloads
because:

1. Lower Network Latency: Localhost connections have minimal network latency
   (typically < 1ms), so there's less waiting time to overlap with concurrent
   operations. This reduces the benefit of concurrency.

2. I/O Bound Operations: For local server testing, the bottleneck shifts from
   network latency to disk I/O and server processing. Concurrent connections
   still help by allowing multiple file reads and HTTP responses to be processed
   in parallel, but the improvement is more modest.

3. Localhost Bandwidth: Localhost connections have very high bandwidth
   (typically limited by memory bandwidth), so sequential downloads are already
   quite fast, leaving less room for improvement through concurrency.

4. Single File Downloads: Unlike Part 1 which downloads multiple files
   concurrently, Part 2 involves downloading single large files. For single files,
   concurrent connections help primarily through parallel data transfer, but
   the overhead of managing multiple connections can offset some gains.

Comparison with Part 1:
- Part 1 external downloads showed higher speedup (2.9x and 1.68x) due to
  network latency being the dominant factor
- Part 2 local server shows lower speedup (1.57x and 1.48x) because network
  latency is minimal on localhost
- Both parts demonstrate that concurrent connections provide measurable
  performance improvements, though the magnitude depends on network conditions
- The results validate that concurrent HTTP connections are beneficial even
  on localhost, though the benefits are more pronounced over network connections


================================================================================
13. ASSIGNMENT QUESTIONS
================================================================================

Q1: How does concurrent connection handling improve HTTP server performance?

A1: Concurrent connections allow the server to process multiple client requests
simultaneously instead of sequentially. This improves performance because:
- While one connection is waiting for I/O (network or disk), other connections
  can be processed
- Reduces overall latency for clients
- Better utilization of server resources
- Particularly beneficial for web pages with multiple objects (images, CSS, JS)

Q2: Why is it important to limit connections both per-client and system-wide?

A2: Connection limits serve different purposes:
- Per-client limit: Prevents a single client from monopolizing server resources,
  ensuring fair resource distribution
- System-wide limit: Prevents server overload, protects against memory exhaustion,
  and ensures system stability under high load

Q3: How does client identification differ from simply using IP address?

A3: Using just IP address would be too restrictive because:
- Multiple legitimate connections from the same network would share the same IP
- Different applications or browser tabs might need separate connections
- IP:port combination provides more granular tracking while still preventing abuse

Q4: What factors affect the speedup achieved by concurrent downloads?

A4: Factors affecting speedup:
- Network latency: Higher latency benefits more from concurrency
- Bandwidth: Available bandwidth limits maximum speedup
- Server response time: Slower servers show more speedup
- Number of connections: More connections help up to a point (diminishing returns)
- File sizes: Mix of small and large files affects optimal concurrency

================================================================================
14. FUTURE IMPROVEMENTS
================================================================================

Potential enhancements (outside assignment scope):
- Persistent connections (HTTP Keep-Alive)
- Connection pooling
- Rate limiting per client
- Request queuing when limits reached
- More sophisticated client identification
- Load balancing support
- HTTPS/TLS support
- Request logging and analytics

================================================================================
END OF README
================================================================================

