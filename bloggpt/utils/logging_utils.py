import logging
import os

import streamlit as st
from ansi2html import Ansi2HTMLConverter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys

import streamlit as st

conv = Ansi2HTMLConverter()


class StreamlitPrint:
    def write(self, s):
        # Check if html span
        if s.startswith("<span"):
            st.markdown(s, unsafe_allow_html=True)
        else:
            html_text = conv.convert(s, full=False)
            st.markdown(html_text, unsafe_allow_html=True)

    def flush(self):
        pass


# Define the colors
class LogColors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"


# Define a custom formatter
class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            color = LogColors.BLUE
        elif record.levelno == logging.INFO:
            color = LogColors.GREEN
        elif record.levelno == logging.WARNING:
            color = LogColors.WARNING
        elif record.levelno == logging.ERROR:
            color = LogColors.FAIL
        else:
            color = LogColors.END
        return color + super().format(record) + LogColors.END


class StreamlitHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        st.write(log_entry)
