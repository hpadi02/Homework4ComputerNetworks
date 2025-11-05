@echo off
REM ==========================================
REM Part 1: External Downloads Testing
REM Teammate 1 Workload - Windows Version
REM ==========================================

echo.
echo ==========================================
echo Part 1: External Downloads Testing
echo Teammate 1 Workload
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3 from python.org
    pause
    exit /b 1
)

REM Step 1: Check for test scripts
echo Step 1: Checking for test scripts...
echo -----------------------------------
if not exist testscript1.txt (
    echo ERROR: testscript1.txt not found!
    echo Please download from: https://zechuncao.com/teaching/csci4406/testfiles/testscript1.txt
    echo.
    pause
    exit /b 1
) else (
    echo [OK] testscript1.txt found
)

if not exist testscript2.txt (
    echo ERROR: testscript2.txt not found!
    echo Please download from: https://zechuncao.com/teaching/csci4406/testfiles/testscript2.txt
    echo.
    pause
    exit /b 1
) else (
    echo [OK] testscript2.txt found
)

REM Check for client script
if not exist http_client_conc.py (
    echo ERROR: http_client_conc.py not found!
    echo Please make sure the file is in the same directory.
    echo.
    pause
    exit /b 1
) else (
    echo [OK] http_client_conc.py found
)

echo.

REM Step 2: Create output directories
echo Step 2: Creating output directories...
echo -----------------------------------
mkdir seq_output1 2>nul
mkdir seq_output2 2>nul
mkdir conc_output1 2>nul
mkdir conc_output2 2>nul
echo [OK] Directories created
echo.

REM Step 3: Run Sequential Downloads
echo ==========================================
echo Step 3: Running SEQUENTIAL downloads
echo ==========================================
echo.

echo Testing testscript1.txt (Sequential)...
echo -----------------------------------
python http_client_conc.py -f testscript1.txt -sequential -o seq_output1 -v > seq1_log.txt 2>&1
if errorlevel 1 (
    echo [ERROR] Sequential test 1 failed!
    type seq1_log.txt
    pause
    exit /b 1
)
echo [OK] Sequential testscript1 complete
echo.

echo Testing testscript2.txt (Sequential)...
echo -----------------------------------
python http_client_conc.py -f testscript2.txt -sequential -o seq_output2 -v > seq2_log.txt 2>&1
if errorlevel 1 (
    echo [ERROR] Sequential test 2 failed!
    type seq2_log.txt
    pause
    exit /b 1
)
echo [OK] Sequential testscript2 complete
echo.

REM Step 4: Run Concurrent Downloads
echo ==========================================
echo Step 4: Running CONCURRENT downloads (10 connections)
echo ==========================================
echo.

echo Testing testscript1.txt (Concurrent)...
echo -----------------------------------
python http_client_conc.py -f testscript1.txt -c 10 -o conc_output1 -v > conc1_log.txt 2>&1
if errorlevel 1 (
    echo [ERROR] Concurrent test 1 failed!
    type conc1_log.txt
    pause
    exit /b 1
)
echo [OK] Concurrent testscript1 complete
echo.

echo Testing testscript2.txt (Concurrent)...
echo -----------------------------------
python http_client_conc.py -f testscript2.txt -c 10 -o conc_output2 -v > conc2_log.txt 2>&1
if errorlevel 1 (
    echo [ERROR] Concurrent test 2 failed!
    type conc2_log.txt
    pause
    exit /b 1
)
echo [OK] Concurrent testscript2 complete
echo.

REM Step 5: Extract timing data
echo ==========================================
echo Step 5: Extracting Results
echo ==========================================
echo.

REM Extract times from log files
for /f "tokens=3" %%a in ('findstr /C:"Total time:" seq1_log.txt') do set SEQ1_TIME=%%a
for /f "tokens=3" %%a in ('findstr /C:"Total time:" conc1_log.txt') do set CONC1_TIME=%%a
for /f "tokens=3" %%a in ('findstr /C:"Total time:" seq2_log.txt') do set SEQ2_TIME=%%a
for /f "tokens=3" %%a in ('findstr /C:"Total time:" conc2_log.txt') do set CONC2_TIME=%%a

echo Extracted Times:
echo   Test 1 Sequential:  %SEQ1_TIME% seconds
echo   Test 1 Concurrent:  %CONC1_TIME% seconds
echo   Test 2 Sequential:  %SEQ2_TIME% seconds
echo   Test 2 Concurrent:  %CONC2_TIME% seconds
echo.

REM Step 6: Calculate speedup using Python
echo Step 6: Calculating speedup...
echo -----------------------------------

python -c "seq1=%SEQ1_TIME%; conc1=%CONC1_TIME%; print('Test 1 Speedup: {:.2f}x'.format(seq1/conc1))" > speedup_temp.txt 2>nul
python -c "seq2=%SEQ2_TIME%; conc2=%CONC2_TIME%; print('Test 2 Speedup: {:.2f}x'.format(seq2/conc2))" >> speedup_temp.txt 2>nul

if exist speedup_temp.txt (
    type speedup_temp.txt
    for /f "tokens=3" %%a in ('findstr "Test 1" speedup_temp.txt') do set SPEEDUP1=%%a
    for /f "tokens=3" %%a in ('findstr "Test 2" speedup_temp.txt') do set SPEEDUP2=%%a
    del speedup_temp.txt
) else (
    echo [WARNING] Could not calculate speedup automatically
    echo Please calculate manually: Sequential_Time / Concurrent_Time
    set SPEEDUP1=[CALCULATE MANUALLY]
    set SPEEDUP2=[CALCULATE MANUALLY]
)

echo.

REM Step 7: Generate results file for README
echo Step 7: Generating results for README.txt...
echo -----------------------------------

(
echo Part 1: External Downloads
echo ---------------------------
echo Testscript1.txt:
echo - Sequential time: %SEQ1_TIME% seconds
echo - Concurrent time ^(10 connections^): %CONC1_TIME% seconds
echo - Speedup: %SPEEDUP1%
echo.
echo Testscript2.txt:
echo - Sequential time: %SEQ2_TIME% seconds
echo - Concurrent time ^(10 connections^): %CONC2_TIME% seconds
echo - Speedup: %SPEEDUP2%
echo.
echo Analysis:
echo The concurrent downloads showed a speedup of %SPEEDUP1% for testscript1 and %SPEEDUP2%
echo for testscript2. This speedup is achieved because:
echo.
echo 1. Network Latency: While one connection is waiting for server response,
echo    other connections can continue downloading, reducing overall wait time.
echo.
echo 2. Concurrent Request Processing: Multiple HTTP requests are sent simultaneously,
echo    allowing the client to utilize available bandwidth more efficiently.
echo.
echo 3. Server Response Time: If the server takes time to process each request,
echo    concurrent connections allow multiple requests to be processed in parallel.
echo.
echo The speedup may vary based on:
echo - Network conditions and latency
echo - Server response times
echo - File sizes in the test scripts
echo - Available bandwidth
echo - Number of concurrent connections ^(10 in this test^)
echo.
echo Factors that could limit speedup:
echo - Bandwidth saturation: Too many connections can saturate available bandwidth
echo - Server rate limiting: Some servers limit connections per client
echo - Connection overhead: Each connection has setup/teardown costs
echo - Small file sizes: For very small files, connection overhead dominates
) > part1_results.txt

echo [OK] Results saved to part1_results.txt
echo.

REM Display summary
echo ==========================================
echo RESULTS SUMMARY
echo ==========================================
echo.
echo TESTSCRIPT1.TXT:
echo   Sequential time:  %SEQ1_TIME% seconds
echo   Concurrent time:  %CONC1_TIME% seconds
echo   Speedup:          %SPEEDUP1%
echo.
echo TESTSCRIPT2.TXT:
echo   Sequential time:  %SEQ2_TIME% seconds
echo   Concurrent time:  %CONC2_TIME% seconds
echo   Speedup:          %SPEEDUP2%
echo.
echo ==========================================
echo ALL TESTS COMPLETE!
echo ==========================================
echo.
echo Next steps:
echo 1. Review the log files: seq1_log.txt, seq2_log.txt, conc1_log.txt, conc2_log.txt
echo 2. Check downloaded files in directories: seq_output1, seq_output2, conc_output1, conc_output2
echo 3. Copy contents from part1_results.txt into README.txt Section 12
echo 4. Add any additional analysis or observations you noticed
echo.
echo Great job completing Part 1!
echo.
pause