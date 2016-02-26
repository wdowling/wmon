from distutils.core import setup

setup(
    name = "wmon",
    version = "0.1.0",
    packages = ['wmon'],

    author = "William Dowling",
    author_email = "wmdowling@gmail.com",
    description = "Website traffic monitor.",
    url = "https://github.com/wdowling/wmon",

    scripts = [
        'bin/wmon',
    ],
)
