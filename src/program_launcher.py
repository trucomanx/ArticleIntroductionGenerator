#!/usr/bin/python3

'''
python3 -m venv venv-temporal

## ubuntu ##
source venv-temporal/bin/activate
pip install --upgrade pip

## windows ##
venv-temporal\Scripts\activate
python -m pip install --upgrade pip

pip install pyinstaller pyinstaller-hooks-contrib
pip install -r requirements.txt
cd src

## ubuntu ##
python3 -m PyInstaller --onefile --windowed --name article_introduction_generator --add-data "article_introduction_generator/icons:icons" --collect-all PyQt5  program_launcher.py


## windows ##
python -m PyInstaller --onefile --windowed --name article_introduction_generator --add-data "article_introduction_generator/icons;icons" --collect-all PyQt5  program_launcher.py

'''

from article_introduction_generator.program import main

if __name__ == "__main__":
    main()

