#!/usr/bin/env python3
"""
Concurrent HTTP Client - Homework 4 (FIXED VERSION)
Fixed issues with hanging concurrent downloads
"""

import socket
import argparse
import sys
import time
import threading
import os
from urllib.parse import urlparse
from typing import List, Tuple
import queue
import ssl

def parse_url(url: str) -> Tuple[str, str, int, str]:
    """Parse URL into components."""
    parsed = urlparse(url)
    
    hostname = parsed.hostname
    if not hostname:
        raise ValueError(f"Invalid URL: {url}")
    
    path = parsed.path or '/'
    if parsed.query:
        path += '?' + parsed.query
    
    port = parsed.port
    if not port:
        port = 443 if parsed.scheme == 'https' else 80
    
    scheme = parsed.scheme or 'http'
    
    return (hostname, path, port, scheme)


def download_file(url: str, output_path: str = None, verbose: bool = False) -> Tuple[bool, float, int]:
    """Download a single file from URL."""
    try:
        start_time = time.time()
        
        # Parse URL
        hostname, path, port, scheme = parse_url(url)
        
        if verbose:
            print(f"[DEBUG] Connecting to {hostname}:{port} ({scheme})")
        
        # Create socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(30)  # 30 second timeout
        
        # HTTPS support
        if scheme == 'https':
            context = ssl.create_default_context()
            client_socket = context.wrap_socket(client_socket, server_hostname=hostname)
            
        try:
            client_socket.connect((hostname, port))
            
            if verbose:
                print(f"[DEBUG] Connected, sending request for {path}")
            
            # Send HTTP GET request
            request = f"GET {path} HTTP/1.1\r\n"
            request += f"Host: {hostname}\r\n"
            request += "Connection: close\r\n"
            request += "\r\n"
            
            client_socket.sendall(request.encode('utf-8'))
            
            # Receive response
            response_data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
            
            # Parse response
            response_str = response_data.decode('utf-8', errors='ignore')
            header_end = response_str.find('\r\n\r\n')
            
            if header_end == -1:
                print(f"Error: Invalid response from {url}", file=sys.stderr)
                return (False, 0, 0)
            
            headers = response_str[:header_end]
            body = response_data[header_end + 4:]
            
            # Check status code
            status_line = headers.split('\r\n')[0]
            if not status_line.startswith('HTTP/1.'):
                print(f"Error: Invalid HTTP response from {url}", file=sys.stderr)
                return (False, 0, 0)
            
            status_code = int(status_line.split()[1])
            
            if status_code != 200:
                print(f"Error: HTTP {status_code} from {url}", file=sys.stderr)
                return (False, 0, 0)
            
            # Determine output path
            if not output_path:
                filename = os.path.basename(path)
                if not filename or filename == '/':
                    filename = 'index.html'
                output_path = filename
            
            # Save file
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(body)
            
            download_time = time.time() - start_time
            file_size = len(body)
            
            if verbose:
                print(f"Downloaded {url} -> {output_path} ({file_size} bytes, {download_time:.2f}s)")
            
            return (True, download_time, file_size)
            
        finally:
            client_socket.close()
            
    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return (False, 0, 0)


def download_worker(url_queue: queue.Queue, output_dir: str, results: List, verbose: bool, worker_id: int):
    """Worker thread for concurrent downloads - FIXED VERSION"""
    if verbose:
        print(f"[Worker {worker_id}] Started")
    
    while True:
        try:
            # Use timeout to prevent infinite blocking
            try:
                url = url_queue.get(timeout=1)
            except queue.Empty:
                if verbose:
                    print(f"[Worker {worker_id}] Queue empty, checking for termination...")
                continue
            
            # Check for termination signal
            if url is None:
                if verbose:
                    print(f"[Worker {worker_id}] Received termination signal")
                url_queue.task_done()
                break
            
            if verbose:
                print(f"[Worker {worker_id}] Processing: {url}")
            
            # Generate output filename
            filename = os.path.basename(urlparse(url).path)
            if not filename or filename == '/':
                filename = f"file_{hash(url) % 10000}.html"
            
            output_path = os.path.join(output_dir, filename) if output_dir else filename
            
            # Download the file
            success, elapsed, size = download_file(url, output_path, verbose)
            
            # Store result (thread-safe list append)
            results.append((url, success, elapsed, size))
            
            if verbose:
                status = "SUCCESS" if success else "FAILED"
                print(f"[Worker {worker_id}] {status}: {url} ({size} bytes, {elapsed:.2f}s)")
            
            # Mark task as done
            url_queue.task_done()
            
        except Exception as e:
            print(f"[Worker {worker_id}] Unexpected error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            try:
                url_queue.task_done()
            except:
                pass
    
    if verbose:
        print(f"[Worker {worker_id}] Terminated")


def download_concurrent(urls: List[str], num_connections: int, output_dir: str = None, verbose: bool = False) -> Tuple[float, List]:
    """Download multiple URLs concurrently - FIXED VERSION"""
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create queue and add URLs
    url_queue = queue.Queue()
    for url in urls:
        url_queue.put(url)
    
    print(f"Starting concurrent download of {len(urls)} URLs with {num_connections} connections...")
    
    # Thread-safe results list
    results = []
    threads = []
    
    start_time = time.time()
    
    # Determine actual number of threads to create
    num_threads = min(num_connections, len(urls))
    
    # Create worker threads
    for i in range(num_threads):
        thread = threading.Thread(
            target=download_worker,
            args=(url_queue, output_dir, results, verbose, i),
            daemon=False  # Don't use daemon threads
        )
        thread.start()
        threads.append(thread)
        if verbose:
            print(f"Created worker thread {i}")
    
    print(f"Waiting for {num_threads} workers to complete...")
    
    # Wait for all downloads to complete with timeout
    try:
        # Wait for queue to be empty (all tasks done)
        while not url_queue.empty():
            time.sleep(0.1)
        
        # Wait a bit more to ensure last tasks are marked done
        url_queue.join()
        
        print("All downloads complete, signaling workers to stop...")
        
        # Signal threads to stop
        for i in range(num_threads):
            url_queue.put(None)
        
        # Wait for threads to finish
        for i, thread in enumerate(threads):
            thread.join(timeout=5)
            if thread.is_alive():
                print(f"Warning: Thread {i} did not terminate cleanly", file=sys.stderr)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user, stopping workers...")
        # Signal all threads to stop
        for _ in threads:
            try:
                url_queue.put(None)
            except:
                pass
        raise
    
    total_time = time.time() - start_time
    
    return (total_time, results)


def download_sequential(urls: List[str], output_dir: str = None, verbose: bool = False) -> Tuple[float, List]:
    """Download multiple URLs sequentially."""
    results = []
    start_time = time.time()
    
    print(f"Starting sequential download of {len(urls)} URLs...")
    
    for i, url in enumerate(urls):
        if verbose:
            print(f"[{i+1}/{len(urls)}] Downloading {url}")
        
        # Generate output filename
        filename = os.path.basename(urlparse(url).path)
        if not filename or filename == '/':
            filename = f"file_{i}.html"
        
        output_path = os.path.join(output_dir, filename) if output_dir else filename
        
        success, elapsed, size = download_file(url, output_path, verbose)
        results.append((url, success, elapsed, size))
    
    total_time = time.time() - start_time
    
    return (total_time, results)


def read_urls_from_file(filepath: str) -> List[str]:
    """Read URLs from a text file (one URL per line)."""
    urls = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    except Exception as e:
        print(f"Error reading URL file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    
    return urls


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='HTTP Client for concurrent/sequential downloads',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-u', '--url', type=str,
                       help='Single URL to download')
    parser.add_argument('-f', '--file', type=str,
                       help='File containing URLs (one per line)')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file or directory')
    parser.add_argument('-c', '--concurrent', type=int, default=10,
                       help='Number of concurrent connections (default: 10)')
    parser.add_argument('-sequential', action='store_true',
                       help='Download sequentially instead of concurrently')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.url and not args.file:
        print("Error: Must specify either -u (URL) or -f (file)", file=sys.stderr)
        sys.exit(1)
    
    if args.url and args.file:
        print("Error: Cannot specify both -u and -f", file=sys.stderr)
        sys.exit(1)
    
    # Single URL download
    if args.url:
        success, elapsed, size = download_file(args.url, args.output, args.verbose)
        if success:
            print(f"Downloaded {size} bytes in {elapsed:.2f} seconds")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Multiple URL download
    urls = read_urls_from_file(args.file)
    if not urls:
        print("Error: No URLs found in file", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(urls)} URLs in {args.file}")
    
    try:
        if args.sequential:
            total_time, results = download_sequential(urls, args.output, args.verbose)
            mode = "Sequential"
        else:
            total_time, results = download_concurrent(urls, args.concurrent, args.output, args.verbose)
            mode = f"Concurrent ({args.concurrent} connections)"
        
        # Print summary
        successful = sum(1 for _, success, _, _ in results if success)
        total_size = sum(size for _, success, _, size in results if success)
        
        print(f"\n{mode} Download Summary:")
        print(f"  Total URLs: {len(urls)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(urls) - successful}")
        print(f"  Total time: {total_time:.2f} seconds")
        print(f"  Total size: {total_size} bytes")
        if successful > 0 and total_time > 0:
            print(f"  Average speed: {total_size / total_time / 1024:.2f} KB/s")
        elif successful > 0:
            print("  Average speed: N/A (time was near zero)")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user!")
        sys.exit(1)


if __name__ == '__main__':
    main()