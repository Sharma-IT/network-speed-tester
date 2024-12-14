import requests
import time
import os
import platform
from tqdm import tqdm
from requests.exceptions import RequestException
import argparse
import aiohttp
import asyncio
import random
import math

def test_download_speed(url, size_in_bytes=10000000, retries=3, backoff_factor=0.3):
    for i in range(retries):
        try:
            start_time = time.time()
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            total_bytes = 0
            total_length = int(response.headers.get('content-length', 0)) or size_in_bytes

            with tqdm(total=total_length, unit='B', unit_scale=True, desc="Downloading") as pbar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        total_bytes += len(chunk)
                        pbar.update(len(chunk))

            elapsed_time = time.time() - start_time
            download_speed = (total_bytes / elapsed_time) / 1_000_000  # Convert to Mbps

            return download_speed
        except RequestException as e:
            if i == retries - 1:
                print(f"Error during download after {retries} retries: {e}")
                return None
            else:
                sleep_time = backoff_factor * (2 ** i) + random.uniform(0, 1)
                print(f"Download attempt {i + 1} failed: {e}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)

def test_upload_speed(url, size_in_bytes=10000000, retries=3, backoff_factor=0.3):
    for i in range(retries):
        try:
            start_time = time.time()
            dummy_data = os.urandom(size_in_bytes)

            with tqdm(total=size_in_bytes, unit='B', unit_scale=True, desc="Uploading") as pbar:
                response = requests.post(url, data=dummy_data, headers={'Content-Length': str(size_in_bytes)})
                pbar.update(size_in_bytes)

            elapsed_time = time.time() - start_time
            upload_speed = (size_in_bytes / elapsed_time) / 1_000_000  # Convert to Mbps

            return upload_speed
        except RequestException as e:
            if i == retries - 1:
                print(f"Error during upload after {retries} retries: {e}")
                return None
            else:
                sleep_time = backoff_factor * (2 ** i) + random.uniform(0, 1)
                print(f"Upload attempt {i + 1} failed: {e}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)

def test_ping(host="8.8.8.8"):
    try:
        ping_cmd = "ping -c 4" if platform.system().lower() != "windows" else "ping -n 4"
        ping_output = os.popen(f"{ping_cmd} {host}").read()

        if "min/avg/max" in ping_output:
            ping_time = ping_output.split("/")[-3]  # For Unix-based systems
        elif "Average" in ping_output:
            ping_time = ping_output.split("Average = ")[1].split("ms")[0]  # For Windows
        else:
            raise ValueError("Unexpected ping output format")

        return float(ping_time)
    except Exception as e:
        print(f"Error while testing ping: {e}")
        return None

async def test_download_speed_async(url, size_in_bytes=10000000, retries=3, backoff_factor=0.3):
    for i in range(retries):
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()

                    total_bytes = 0
                    total_length = int(response.headers.get('content-length', 0)) or size_in_bytes

                    with tqdm(total=total_length, unit='B', unit_scale=True, desc="Downloading (Async)") as pbar:
                        async for chunk in response.content.iter_chunked(1024):
                            if chunk:
                                total_bytes += len(chunk)
                                pbar.update(len(chunk))

                    elapsed_time = time.time() - start_time
                    download_speed = (total_bytes / elapsed_time) / 1_000_000  # Convert to Mbps

                    return download_speed
        except aiohttp.ClientError as e:
            if i == retries - 1:
                print(f"Error during async download after {retries} retries: {e}")
                return None
            else:
                sleep_time = backoff_factor * (2 ** i) + random.uniform(0, 1)
                print(f"Async download attempt {i + 1} failed: {e}. Retrying in {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)

def main():
    parser = argparse.ArgumentParser(description="Network Speed Testing Script")
    parser.add_argument('--url', type=str, default="http://speedtest.tele2.net/10MB.zip", help='Test URL')
    parser.add_argument('--file_size', type=int, default=10_000_000, help='Size of upload file in bytes')
    parser.add_argument('--test', type=str, choices=['download', 'upload', 'ping', 'all', 'async'], default='all', help='Type of test to run')

    args = parser.parse_args()

    if args.test in ['download', 'all']:
        download_speed = test_download_speed(args.url, size_in_bytes=args.file_size)
        if download_speed is not None:
            print(f"Download Speed: {download_speed:.2f} Mbps")

    if args.test in ['upload', 'all']:
        upload_speed = test_upload_speed(args.url, size_in_bytes=args.file_size)
        if upload_speed is not None:
            print(f"Upload Speed: {upload_speed:.2f} Mbps")

    if args.test in ['ping', 'all']:
        ping_time = test_ping()
        if ping_time is not None:
            print(f"Ping: {ping_time:.2f} ms")

    if args.test == 'async':
        download_speed = asyncio.run(test_download_speed_async(args.url, size_in_bytes=args.file_size))
        if download_speed is not None:
            print(f"Download Speed (Async): {download_speed:.2f} Mbps")

if __name__ == "__main__":
    main()
