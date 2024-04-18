import os
import sys
import subprocess
import requests
import argparse
import logging
import traceback
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from config import config_load
import speedtest
from networkspeed import display_network_speed
import json
import time
