from setuptools import setup, find_packages
import os

def package_files(directories):
    paths = []
    for directory in directories:
        for (path, _, filenames) in os.walk(directory):
            for filename in filenames:
                paths.append(os.path.join(path, filename))
    return paths

data_files = package_files(["meti/fonts/", "meti/icons/", "meti/style/"])
data_files.append("./meti/schema.sql")

setup(
    name='Meti',
    version='0.8.0',
    packages=[
        "meti", 
        "meti.gui",
        "meti.gui.widgets",
        "meti.db",
        "meti.scripts"
    ],
    package_data={
        'meti': [
            'fonts/*.ttf',
            'icons/*.png',
            'style/*.scss',
            'schema.sql'
        ],
    },
    include_package_data=True,
    install_requires=[
        'pyside6>=6.8.0.2',
        'pysqlcipher3>=1.2.0',
        'pillow>=11.0.0'
    ],
    entry_points={
        'gui_scripts': [
            'Meti = meti.app:main',
        ],
    },
)
