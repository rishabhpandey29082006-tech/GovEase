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

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({

        "status": "success",

        "message":
            "GovEase Government Benefits API is running"

    })


# =========================================================
# OPTIONS / CORS PREFLIGHT
# =========================================================

@app.route(
    "/api/check-eligibility",
    methods=["OPTIONS"]
)
def eligibility_options():

    return "", 204


# =========================================================
# GET ALL SCHEMES
# =========================================================

@app.route(
    "/api/schemes",
    methods=["GET"]
)
def get_schemes():

    schemes = load_schemes()

    return jsonify({

        "status": "success",

        "total_schemes":
            len(schemes),

        "schemes":
            schemes

    })


# =========================================================
# DOCUMENT UPLOAD
# =========================================================

@app.route(
    "/api/upload-document",
    methods=["POST"]
)
def upload_document():

    try:

        if "file" not in request.files:

            return jsonify({

                "status": "error",

                "message":
                    "No document received."

            }), 400


        file = request.files["file"]


        if not file.filename:

            return jsonify({

                "status": "error",

                "message":
                    "No file selected."

            }), 400


        if not allowed_file(
            file.filename
        ):

            return jsonify({

                "status": "error",

                "message":
                    "Only JPG, JPEG, PNG and PDF files are allowed."

            }), 400


        original_name = secure_filename(
            file.filename
        )


        if "." not in original_name:

            return jsonify({

                "status": "error",

                "message":
                    "Invalid filename."

            }), 400


        extension = (
            original_name
            .rsplit(".", 1)[1]
            .lower()
        )


        random_name = (
            uuid.uuid4().hex
            + "."
            + extension
        )


        file_path = os.path.join(
            UPLOAD_FOLDER,
            random_name
        )


        file.save(file_path)


        return jsonify({

            "status": "success",

            "message":
                "Document uploaded successfully.",

            "document": {

                "original_name":
                    original_name,

                "server_name":
                    random_name,

                "document_type":
                    extension

            }

        })


    except Exception as error:

        print(
            "Upload error:",
            error
        )

        return jsonify({

            "status": "error",

            "message":
                "Document upload failed."

        }), 500


# =========================================================
# ELIGIBILITY ENGINE
# =========================================================

@app.route(
    "/api/check-eligibility",
    methods=["POST"]
)
def check_eligibility():

    try:

        user = request.get_json(
            silent=True
        )


        if not user:

            return jsonify({

                "status": "error",

                "message":
                    "User profile not received."

            }), 400


        schemes = load_schemes()


        if not schemes:

            return jsonify({

                "status": "error",

                "message":
                    "No schemes found in schemes.json."

            }), 404


        # Run eligibility engine

        results = check_all_schemes(
            user,
            schemes
        )


        if not isinstance(
            results,
            list
        ):

            results = []


        # Sort by highest eligibility

        results.sort(

            key=lambda item:
                item.get(
                    "eligibility_percentage",
                    0
                ),

            reverse=True

        )


        # =================================================
        # CLASSIFICATION
        # =================================================

        eligible = [

            item

            for item in results

            if item.get(
                "eligibility_percentage",
                0
            ) >= 70

        ]


        possible = [

            item

            for item in results

            if 40 <= item.get(
                "eligibility_percentage",
                0
            ) < 70

        ]


        not_eligible = [

            item

            for item in results

            if item.get(
                "eligibility_percentage",
                0
            ) < 40

        ]


        # =================================================
        # FINAL RESPONSE
        # =================================================

        return jsonify({

            "status": "success",

            "profile": user,

            "total_schemes_checked":
                len(schemes),

            "summary": {

                "eligible":
                    len(eligible),

                "possible":
                    len(possible),

                "not_eligible":
                    len(not_eligible)

            },

            "schemes":
                results

        })


    except Exception as error:

        print(
            "Eligibility error:",
            error
        )

        return jsonify({

            "status": "error",

            "message":
                "Eligibility calculation failed.",

            "error":
                str(error)

        }), 500


# =========================================================
# FILE TOO LARGE
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({

        "status": "error",

        "message":
            "File is too large. Maximum allowed size is 5 MB."

    }), 413


# =========================================================
# GENERAL ERROR
# =========================================================

@app.errorhandler(500)
def server_error(error):

    return jsonify({

        "status": "error",

        "message":
            "Internal server error."

    }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("       GovEase Government Benefits")
    print("======================================")
    print(
        "GovEase backend is starting..."
    )
    print(
        "API: /api/schemes"
    )
    print(
        "Eligibility: /api/check-eligibility"
    )
    print(
        "Upload: /api/upload-document"
    )
    print("======================================")


    host = "0.0.0.0"

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(

        host=host,

        port=port,

        debug=False,

        use_reloader=False

    )