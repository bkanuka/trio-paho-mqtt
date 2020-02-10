from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='trio-paho-mqtt',  # Required
    version='0.3.1',  # Required
    description='trio async MQTT Client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bkanuka/trio-paho-mqtt',
    download_url='https://github.com/bkanuka/trio-paho-mqtt/archive/v0.3.1.tar.gz',
    author_email='bkanuka@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Trio',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='trio mqtt',
    packages=["trio_paho_mqtt"],
    python_requires='>=3.5, <4',
    install_requires=['paho-mqtt', 'trio'],
    project_urls={
        'Source': 'https://github.com/bkanuka/trio-paho-mqtt',
    },
)
