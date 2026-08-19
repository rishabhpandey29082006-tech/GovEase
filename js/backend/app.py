from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import json
import os
import uuid

from eligibility import check_all_schemes


# =========================================================
# GOV EASE BACKEND
# =========================================================

app = Flask(__name__)


# =========================================================
# CORS CONFIGURATION
# =========================================================
# Allows the GitHub Pages frontend to communicate
# with the Render backend.

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "https://rishabhpandey29082006-tech.github.io"
            ],
            "methods": [
                "GET",
                "POST",
                "OPTIONS"
            ],
            "allow_headers": [
                "Content-Type"
            ]
        }
    }
)


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SCHEMES_FILE = os.path.join(
    BASE_DIR,
    "schemes.json"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "secure_uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# FILE SECURITY
# =========================================================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "pdf"
}

MAX_FILE_SIZE = 5 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =========================================================
# LOAD SCHEMES
# =========================================================

def load_schemes():

    try:

        with open(
            SCHEMES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get(
                "schemes",
                []
            )

        return []

    except Exception as error:

        print(
            "Scheme loading error:",
            error
        )

        return []


# =========================================================
# HOME / HEALTH CHECK
# =========================================================

