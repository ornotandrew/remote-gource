import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='remote-gource',
    version='0.0.1',
    author='Andrew van Rooyen',
    author_email='wraith.andrew@gmail.com',
    description='A wrapper around Gource which can read commits from third parties (Github etc)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pypa/remote-gource',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
