#!/usr/bin/env python3
"""
Debug script to test HTTP client and diagnose issues
"""

import sys
import os

def test_url_file(filepath):
    """Test if URL file exists and show its contents"""
    print(f"\n{'='*60}")
    print(f"Testing URL file: {filepath}")
    print('='*60)
    
    if not os.path.exists(filepath):
        print(f"❌ ERROR: File '{filepath}' does not exist!")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in current directory:")
        for f in os.listdir('.'):
            print(f"  - {f}")
        return False
    
    print(f"✓ File exists")
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        print(f"✓ File readable")
        print(f"Total lines: {len(lines)}")
        
        # Parse URLs
        urls = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
                print(f"  Line {i}: {line[:80]}{'...' if len(line) > 80 else ''}")
        
        print(f"\nTotal valid URLs: {len(urls)}")
        
        if not urls:
            print("❌ ERROR: No valid URLs found in file!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR reading file: {e}")
        return False


def test_single_url(url):
    """Test downloading a single URL"""
    print(f"\n{'='*60}")
    print(f"Testing single URL download")
    print('='*60)
    print(f"URL: {url}")
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        print(f"✓ URL parsed successfully")
        print(f"  Scheme: {parsed.scheme}")
        print(f"  Hostname: {parsed.hostname}")
        print(f"  Port: {parsed.port or ('443' if parsed.scheme == 'https' else '80')}")
        print(f"  Path: {parsed.path or '/'}")
        
        # Try importing the client module
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import http_client_conc
        
        print(f"\n✓ Client module imported")
        print(f"Attempting download (this may take a moment)...")
        
        success, elapsed, size = http_client_conc.download_file(url, verbose=True)
        
        if success:
            print(f"\n✅ SUCCESS!")
            print(f"  Downloaded: {size} bytes")
            print(f"  Time: {elapsed:.2f} seconds")
            print(f"  Speed: {size/elapsed/1024:.2f} KB/s")
        else:
            print(f"\n❌ DOWNLOAD FAILED")
            
        return success
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main diagnostic function"""
    print("HTTP Client Diagnostic Tool")
    print("="*60)
    
    # Check if testscript files exist
    test_files = ['testscript1.txt', 'testscript2.txt']
    
    print("\nStep 1: Checking for test script files...")
    for tf in test_files:
        if os.path.exists(tf):
            print(f"  ✓ {tf} found")
            test_url_file(tf)
        else:
            print(f"  ✗ {tf} NOT found")
    
    # Test with a simple URL
    print("\n" + "="*60)
    print("Step 2: Testing with a simple URL")
    print("="*60)
    test_url = "http://httpbin.org/get"
    print(f"Testing: {test_url}")
    test_single_url(test_url)
    
    # Provide instructions
    print("\n" + "="*60)
    print("TROUBLESHOOTING GUIDE")
    print("="*60)
    print("""
If downloads aren't starting, try these steps:

1. Make sure you're using python3:
   python3 http_client_conc.py -f testscript1.txt -c 10 -o conc_output1 -v

2. Check if testscript files exist in current directory:
   ls -la testscript*.txt

3. Download the test scripts if missing:
   wget https://zechuncao.com/teaching/csci4406/testfiles/testscript1.txt
   wget https://zechuncao.com/teaching/csci4406/testfiles/testscript2.txt

4. Verify URLs in the file:
   cat testscript1.txt | head -5

5. Test with a single URL first:
   python3 http_client_conc.py -u http://httpbin.org/get -o test.html -v

6. Check for network connectivity:
   ping -c 3 httpbin.org

7. Check for firewall issues if on a restricted network

8. Look for error messages in the output - they'll help identify the issue
""")


if __name__ == '__main__':
    main()