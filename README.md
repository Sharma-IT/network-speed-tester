# Network Speed Tester

This Python script allows you to test your network speed by measuring download speed, upload speed, and ping. It provides both synchronous and asynchronous methods for testing, along with error handling and retries to ensure reliable results.

## Features

- **Download Speed Test**: Measures the download speed by downloading a file from a specified URL.
- **Upload Speed Test**: Measures the upload speed by uploading a dummy file to a specified URL.
- **Ping Test**: Measures the ping (latency) to a specified host.
- **Asynchronous Testing**: Supports asynchronous download speed testing using `aiohttp`.
- **Error Handling and Retries**: Implements retries with exponential backoff to handle temporary network issues.
- **Command-Line Interface**: Provides a user-friendly command-line interface with customizable options.

## Installation

1. **Clone the Repository**:

```bash
git clone https://github.com/Sharma-IT/network-speed-test.git
cd network-speed-test
```

2. **Install Required Libraries**:

```bash
pip install requests tqdm aiohttp argparse
```  

## Usage

Run the script from the command line with various options:

```bash
python(3) speedtest.py --test all
```

## Available Options:

- `--url`: Specify the test URL (default: `http://speedtest.tele2.net/10MB.zip`).
- `--file_size`: Specify the size of the upload file in bytes (default: `10_000_000`).
- `--test`: Specify the type of test to run. Options are:

  - `download`: Test download speed.
  - `upload`: Test upload speed.
  - `ping`: Test ping.
  - `all`: Test all (download, upload, and ping).
  - `async`: Test download speed asynchronously.
 
## Examples

1. Test All Speeds and Ping:

```bash
python(3) speedtest.py --test all
```

2. Test Download Speed:

```bash
python(3) speedtest.py --test download
```

3. Test Upload Speed:

```bash
python(3) speedtest.py --test upload
```

4. Test Ping:

```bash
python(3) speedtest.py --test ping
```

5. Test Download Speed Asynchronously:

```bash
python(3) speedtest.py --test async
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Make your changes and commit them (git commit -m 'Add some feature').
4. Push to the branch (git push origin feature-branch).
5. Open a pull request.

## License

This project is licensed under the GPL 3.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the contributors of `requests`, `tqdm`, `aiohttp`, and `argparse` for their excellent libraries.
- Inspired by the need for a simple yet robust network speed testing tool.
