# Remote Gource

This is a wrapper around [Gource](https://gource.io/) which pulls commit data from a remote source (e.g. Github, Bitbucket etc).

This makes it easier to generate multi-repo Gource outputs based on a team workspace/organisation.

## Usage

```shell
pip install remote-gource
```

## Building & Deploying

First, build the package.

```shell
python setup.py sdist bdist_wheel
```

Then, upload it to [pypi.org](https://pypi.org).

```shell
twine upload dist/*
```
