from setuptools import setup, find_packages


setup(
    name='jukebox',
    version='0.01',
    author='Jason Michalski',
    author_email='armooo@armooo.net',
    packages=find_packages(exclude=['tests']),
    install_requires=['klein', 'mutagen', 'pyyaml', 'service_identity', 'pyOpenSSL', ],
    package_dir={'jukebox': 'jukebox'},
    package_data={'jukebox': ['static/*']},

)
