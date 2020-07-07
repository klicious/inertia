import os
import sys

# determine if application is a script file or frozen exe
PWD = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)

INPUT_DIRECTORY = os.path.join(PWD, 'input')
OUTPUT_DIRECTORY = os.path.join(PWD, 'output')

OUTPUT_FILE_NAME = 'packet_input.xlsx'
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILE_NAME)