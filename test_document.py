import os
import time
import zipfile
import requests
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.environ["SARVAM_API_KEY"]
)

FILE_NAME = "kannada.png"

with open(FILE_NAME, "rb") as f:
    job = client.doc_ai.digitise(
        file=[(FILE_NAME, f, "image/png")],
        language="kn-IN",
        output_format="md",
    )

print("Job created:", job.job_id)

while True:
    status = client.doc_ai.get_status(job_id=job.job_id)

    print("Status:", status.status)

    if status.status.lower() in {
        "completed",
        "partially_completed",
        "failed",
        "rejected",
    }:
        break

    time.sleep(5)

if status.status.lower() in {"completed", "partially_completed"}:

    download = client.doc_ai.get_download_url(
        job_id=job.job_id
    )

    print("\nOCR completed!")
    print("Downloading result...")

    response = requests.get(download.url)
    response.raise_for_status()

    zip_path = "output/ocr_result.zip"

    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("output/ocr")

    print("OCR result extracted to:")
    print("output/ocr/")

else:
    print("\nDocument processing failed.")