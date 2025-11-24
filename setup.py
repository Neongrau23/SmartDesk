from setuptools import setup, find_packages

setup(
    name="smartdesk",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "psutil",
        "pynput",
        "pywin32"
    ],
    entry_points={
        'console_scripts': [
            'smartdesk=smartdesk.main:main',
        ],
    },
)