# -*- coding: utf-8 -*-


import sys
import os
from app import create_app


reload(sys)
sys.setdefaultencoding('utf-8')

stock = create_app(os.getenv('STOCK_SET') or 'production')
