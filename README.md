# Homework 4: Concurrent Connection HTTP Server

## Overview
This project implements a concurrent HTTP server that can handle multiple client connections simultaneously with configurable connection limits.

## Files

- `http_server_conc` - Main concurrent HTTP server implementation
- `http_client_conc.py` - Python HTTP client for performance testing
- `README.txt` - Detailed assignment documentation and answers

## Quick Start

### Run the Server
```bash
./http_server_conc -p 20001 -maxclient 12 -maxtotal 60
```

### Test with Browser
Open `http://localhost:20001/` in your browser

### Test with Client
```bash
# Single file download
python3 http_client_conc.py -u http://localhost:20001/index.html -o output.html

# Concurrent downloads
python3 http_client_conc.py -f urls.txt -c 10 -o output_dir
```

## Demo Instructions

### Starting the Server

Start the server with the following command:
```bash
./http_server_conc -p 20001 -maxclient 12 -maxtotal 60
```

This starts the server on port 20001, with a maximum of 12 connections per client and 60 total system-wide connections.

### Testing Basic Functionality

With the server running, test it in another terminal:

```bash
# Serve index.html
curl http://localhost:20001/

# Serve another file
curl http://localhost:20001/test.txt

# Test 404 error
curl http://localhost:20001/nonexistent.html
```

### Testing Concurrent Connections

Test multiple concurrent requests:
```bash
curl http://localhost:20001/ &
curl http://localhost:20001/test.txt &
curl http://localhost:20001/ &
wait
```

All requests are processed concurrently, each in its own thread.

### Testing Connection Limits

The server enforces two types of limits:
- Per-client limit: Each client (identified by IP:port) can have at most `-maxclient` connections
- System-wide limit: Total connections across all clients cannot exceed `-maxtotal`

If a limit is exceeded, the server returns HTTP 503 Service Unavailable.

### Testing with HTTP Client

Download files using the HTTP client:
```bash
# Single file download with verbose output
python3 http_client_conc.py -u http://localhost:20001/index.html -o downloaded.html -v

# Sequential downloads from URL list
python3 http_client_conc.py -f testscript1.txt -sequential -o seq_output -v

# Concurrent downloads (10 connections)
python3 http_client_conc.py -f testscript1.txt -c 10 -o conc_output -v
```

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Performance Results

### Part 1: External Downloads
- Testscript1.txt: Sequential 21.97s -> Concurrent 2.55s = 2.9x speedup
- Testscript2.txt: Sequential 16.13s -> Concurrent 9.61s = 1.68x speedup

### Part 2: Local Server
- Testfiles1.tar.gz: Sequential 3.42s -> Concurrent 2.18s = 1.57x speedup
- Testfiles2.tar.gz: Sequential 2.89s -> Concurrent 1.95s = 1.48x speedup

Detailed analysis available in README.txt Section 12.

## Troubleshooting

**"Address already in use"**
```bash
# Find and kill process on port 20001
lsof -ti:20001 | xargs kill -9
# Or use a different port
./http_server_conc -p 20002 -maxclient 12 -maxtotal 60
```

**"Permission denied"**
```bash
chmod +x http_server_conc
```

**"Module not found"**
```bash
# Ensure using Python 3
python3 --version
```

## Requirements
- Python 3.x
- No external dependencies (uses only standard library)

## Team Members
- Hugo Padilla - Server implementation, Part 2 performance evaluation
- Emilio Villar - Part 1 performance evaluation
