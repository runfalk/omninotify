from setuptools import setup

setup(
    name="omninotify",
    version="0.1",
    description="A cross platform desktop notification library for Python",
    url="https://github.com/runfalk/omninotify",
    author="Andreas Runfalk",
    author_email="andreas@runfalk.se",
    license="MIT",
    packages=["omninotify"],
    extras_require={
        ":sys_platform == 'linux2'": [
            "pydbus",
        ]
    },
)
