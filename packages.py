import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import requests
import random
import json
import base64
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode