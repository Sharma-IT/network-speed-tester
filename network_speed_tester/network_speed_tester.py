#!/usr/bin/env python3

"""
Network Speed Tester

A tool for testing network speed including download speed, upload speed, and ping.
Supports both synchronous and asynchronous testing methods with error handling and retries.
"""

import asyncio
import os
import platform
import random
import time
from dataclasses import dataclass
from typing import Optional, Union, Final

import aiohttp
import requests
from requests.exceptions import RequestException
from tqdm import tqdm

# Constants
DEFAULT_URL: Final[str] = "http://speedtest.tele2.net/10MB.zip"
DEFAULT_FILE_SIZE: Final[int] = 10_000_000
DEFAULT_RETRIES: Final[int] = 3
DEFAULT_BACKOFF_FACTOR: Final[float] = 0.3
DEFAULT_CHUNK_SIZE: Final[int] = 1024
DEFAULT_TIMEOUT: Final[int] = 10
DEFAULT_PING_HOST: Final[str] = "8.8.8.8"

@dataclass
class SpeedTestResult:
    """Data class to store speed test results"""
    download_speed: Optional[float] = None
    upload_speed: Optional[float] = None
    ping: Optional[float] = None
    async_download_speed: Optional[float] = None

    def __str__(self) -> str:
        """Format the results for display"""
        results = []
        if self.download_speed is not None:
            results.append(f"Download Speed: {self.download_speed:.2f} Mbps")
        if self.upload_speed is not None:
            results.append(f"Upload Speed: {self.upload_speed:.2f} Mbps")
        if self.ping is not None:
            results.append(f"Ping: {self.ping:.2f} ms")
        if self.async_download_speed is not None:
            results.append(f"Download Speed (Async): {self.async_download_speed:.2f} Mbps")
        return "\n".join(results)

class SpeedTester:
    """Class for testing network speed"""

    def __init__(
        self,
        url: str = DEFAULT_URL,
        file_size: int = DEFAULT_FILE_SIZE,
        retries: int = DEFAULT_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    ):
        """Initialize SpeedTester with configuration parameters"""
        self.url = url
        self.file_size = file_size
        self.retries = retries
        self.backoff_factor = backoff_factor

    def _calculate_speed(self, bytes_transferred: int, elapsed_time: float) -> float:
        """Calculate speed in Mbps"""
        return (bytes_transferred / elapsed_time) / 1_000_000

    def _handle_retry(self, attempt: int, error: Exception) -> float:
        """Handle retry logic with exponential backoff"""
        if attempt == self.retries - 1:
            raise error
        sleep_time = self.backoff_factor * (2 ** attempt) + random.uniform(0, 1)
        print(f"Attempt {attempt + 1} failed: {error}. Retrying in {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        return sleep_time

    def test_download_speed(self) -> Optional[float]:
        """Test download speed using synchronous requests"""
        for i in range(self.retries):
            try:
                start_time = time.time()
                with requests.get(self.url, stream=True, timeout=DEFAULT_TIMEOUT) as response:
                    response.raise_for_status()
                    total_bytes = 0
                    total_length = int(response.headers.get('content-length', 0)) or self.file_size

                    with tqdm(total=total_length, unit='B', unit_scale=True, desc="Downloading") as pbar:
                        for chunk in response.iter_content(chunk_size=DEFAULT_CHUNK_SIZE):
                            if chunk:
                                total_bytes += len(chunk)
                                pbar.update(len(chunk))

                    return self._calculate_speed(total_bytes, time.time() - start_time)
            except RequestException as e:
                try:
                    self._handle_retry(i, e)
                except Exception as e:
                    print(f"Error during download after {self.retries} retries: {e}")
                    return None

    def test_upload_speed(self) -> Optional[float]:
        """Test upload speed using synchronous requests"""
        for i in range(self.retries):
            try:
                dummy_data = os.urandom(self.file_size)
                start_time = time.time()

                with tqdm(total=self.file_size, unit='B', unit_scale=True, desc="Uploading") as pbar:
                    response = requests.post(
                        self.url,
                        data=dummy_data,
                        headers={'Content-Length': str(self.file_size)},
                        timeout=DEFAULT_TIMEOUT
                    )
                    response.raise_for_status()
                    pbar.update(self.file_size)

                return self._calculate_speed(self.file_size, time.time() - start_time)
            except RequestException as e:
                try:
                    self._handle_retry(i, e)
                except Exception as e:
                    print(f"Error during upload after {self.retries} retries: {e}")
                    return None

    def test_ping(self, host: str = DEFAULT_PING_HOST) -> Optional[float]:
        """Test ping to a specified host"""
        try:
            ping_cmd = "ping -c 4" if platform.system().lower() != "windows" else "ping -n 4"
            ping_output = os.popen(f"{ping_cmd} {host}").read()

            if "min/avg/max" in ping_output:
                ping_time = ping_output.split("/")[-3]  # Unix-based systems
            elif "Average" in ping_output:
                ping_time = ping_output.split("Average = ")[1].split("ms")[0]  # Windows
            else:
                raise ValueError("Unexpected ping output format")

            return float(ping_time)
        except Exception as e:
            print(f"Error while testing ping: {e}")
            return None

    async def test_download_speed_async(self) -> Optional[float]:
        """Test download speed using asynchronous requests"""
        for i in range(self.retries):
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.url) as response:
                        response.raise_for_status()
                        total_bytes = 0
                        total_length = int(response.headers.get('content-length', 0)) or self.file_size

                        with tqdm(total=total_length, unit='B', unit_scale=True, desc="Downloading (Async)") as pbar:
                            async for chunk in response.content.iter_chunked(DEFAULT_CHUNK_SIZE):
                                if chunk:
                                    total_bytes += len(chunk)
                                    pbar.update(len(chunk))

                        return self._calculate_speed(total_bytes, time.time() - start_time)
            except aiohttp.ClientError as e:
                if i == self.retries - 1:
                    print(f"Error during async download after {self.retries} retries: {e}")
                    return None
                sleep_time = self.backoff_factor * (2 ** i) + random.uniform(0, 1)
                print(f"Async download attempt {i + 1} failed: {e}. Retrying in {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)

def main() -> None:
    """Main function to handle command line arguments and run tests"""
    import argparse

    parser = argparse.ArgumentParser(description="Network Speed Testing Tool")
    parser.add_argument('--url', type=str, default=DEFAULT_URL, help='Test URL')
    parser.add_argument('--file_size', type=int, default=DEFAULT_FILE_SIZE, help='Size of upload file in bytes')
    parser.add_argument(
        '--test',
        type=str,
        choices=['download', 'upload', 'ping', 'all', 'async'],
        default='all',
        help='Type of test to run'
    )

    args = parser.parse_args()
    tester = SpeedTester(url=args.url, file_size=args.file_size)
    result = SpeedTestResult()

    if args.test in ['download', 'all']:
        result.download_speed = tester.test_download_speed()

    if args.test in ['upload', 'all']:
        result.upload_speed = tester.test_upload_speed()

    if args.test in ['ping', 'all']:
        result.ping = tester.test_ping()

    if args.test == 'async':
        result.async_download_speed = asyncio.run(tester.test_download_speed_async())

    print(result)

if __name__ == "__main__":
    main()
