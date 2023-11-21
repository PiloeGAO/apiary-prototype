"""A utility script to extract the public API to the submitter libs using the OpenAPI generator."""
import logging
import os
import shutil
import subprocess
import sys

# Logger setup.
logger = logging.getLogger("apiary_api_generator")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "Apiary Open API Client Generator | %(levelname)s | %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Project setup.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_FOLDER = os.path.join("clients", "apiary-openapi")
PROJECT_OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, OUTPUT_FOLDER)

HOST = os.environ.get("APIARY_HOST", "http://127.0.0.1")
OPENAPI_YAML = f"{HOST}/openapi.json"

# Commands
GENERATOR_COMMAND = [
    "docker",
    "run",
    "--rm",
    "--network=host",
    "-v",
    f"{PROJECT_ROOT}:/local",
    "openapitools/openapi-generator-cli",
    "generate",
    "-i",
    f"{OPENAPI_YAML}",
    "-g",
    "python",
    "-o",
    f"/local/{OUTPUT_FOLDER}",
    "-c",
    "/local/build_scripts/openapi-config.yaml",
]
BUILD_COMMAND = ["poetry", "build"]


def main():
    """Main execution function."""
    logger.info("Generating the apiary-openapi module from the API (%s).", OPENAPI_YAML)

    if os.path.exists(PROJECT_OUTPUT_FOLDER):
        logger.warning("Cleaning output folder: %s", PROJECT_OUTPUT_FOLDER)
        shutil.rmtree(PROJECT_OUTPUT_FOLDER)
    os.makedirs(PROJECT_OUTPUT_FOLDER)

    logger.debug("Running: %s", " ".join(GENERATOR_COMMAND))
    generator_errors = []
    with subprocess.Popen(
        GENERATOR_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as process:
        for line in process.stdout.readlines():
            logger.debug(line.decode().replace("\n", ""))

        for line in process.stderr.readlines():
            error_line = line.decode().replace("\n", "")
            generator_errors.append(error_line)
            logger.error(error_line)

    if generator_errors:
        logger.critical("Api generation failed. Please check the errors.")
        sys.exit(1)

    logger.info("API generated in: %s", PROJECT_OUTPUT_FOLDER)

    logger.info("Building the wheel file.")

    logger.debug("Running: %s", " ".join(BUILD_COMMAND))
    building_errors = []
    with subprocess.Popen(
        BUILD_COMMAND,
        cwd=PROJECT_OUTPUT_FOLDER,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        for line in process.stdout.readlines():
            logger.debug(line.decode().replace("\n", ""))

        for line in process.stderr.readlines():
            error_line = line.decode().replace("\n", "")

            if "Creating virtualenv apiary-openapi" in error_line:
                # This is not an error but a debug statement detected as error.
                logger.debug(error_line)
                continue

            building_errors.append(error_line)
            logger.error(error_line)

    if building_errors:
        logger.critical("Wheel building failed, Please check the errors.")
        sys.exit(1)

    logger.info("Wheel builded successfully.")


if __name__ == "__main__":
    main()
