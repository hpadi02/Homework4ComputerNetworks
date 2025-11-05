# Homework 4: Concurrent Connection HTTP Server

## Overview
This project implements a concurrent HTTP server that can handle multiple client connections simultaneously with configurable connection limits.

## Files

- `http_server_conc.py` - Main concurrent HTTP server implementation
- `http_client_conc.py` - Python HTTP client for performance testing
- `README.txt` - Detailed assignment documentation and answers
- `TEAM_NOTES.md` - Task distribution and instructions for teammates

## Quick Start

### Run the Server
```bash
python3 http_server_conc.py -p 20001 -maxclient 12 -maxtotal 60
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

## Requirements
- Python 3.x
- No external dependencies (uses only standard library)

## Team Members
- Hugo Padilla - Server implementation
- Emilio Villar - Part 1 performance evaluation
- [Teammate 2] - Part 2 performance evaluation

See `TEAM_NOTES.md` for detailed task distribution.
