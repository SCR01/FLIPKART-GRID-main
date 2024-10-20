import boto3
from PIL import Image
import datetime
import dotenv
import os

dotenv.load_dotenv()

client = boto3.client(
    "textract",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def get_aws_ocr(image_array):
    # convert the image array to image in rgb format
    image = Image.fromarray(image_array).convert("RGB")

    # save the image to a byte array
    imagename = str(datetime.datetime.now()) + "image.jpg"
    image.save(imagename)
    with open(imagename, "rb") as file:
        bytes = bytearray(file.read())

    response = client.detect_document_text(
        Document={
            "Bytes": bytes,
        }
    )

    text = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text += item["Text"] + " "

    return text


# # convert image to bytes
# with open("image.jpg", "rb") as file:
#     bytes = bytearray(file.read())

# response = client.detect_document_text(
#     Document={
#         "Bytes": bytes,
#     }
# )

# text = ""
# for item in response["Blocks"]:
#     if item["BlockType"] == "LINE":
#         text += item["Text"] + " "

# print(text)
