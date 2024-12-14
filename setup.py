from setuptools import setup, find_packages

setup(
    name="network-speed-tester",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "tqdm",
        "aiohttp",
        "argparse"
    ],
    entry_points={
        'console_scripts': [
            'network-speed-tester=network_speed_tester:main',
            'nst=network_speed_tester:main'
        ],
    },
    author="Shubham Sharma",
    author_email="shubhamsharma.emails@gmail.com",
    description="A Python tool for testing network speed including download, upload, and ping tests",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sharma-IT/network-speed-tester",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
