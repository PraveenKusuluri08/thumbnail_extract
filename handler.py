import json
import boto3
import os
from datetime import datetime
from io import BytesIO
from PIL import Image,ImageOps
import uuid

s3 = boto3.client('s3')
size = int(os.environ['THUMBNAIL_SIZE'])

def s3ThumbnailGenerator(event, context):
    print(event)
    bucket =event["Records"][0]['s3']["bucket"]["name"]
    key = event["Records"][0]['s3']["object"]["key"]
    image_size = event["Records"][0]['s3']["object"]["size"]
    if not key.endswith("_thumbnail.png"):
        image = get_s3_image(bucket, key)
        
        thumbnail = image_to_thumbnail(image)
        thumbname_key = new_filename(key)
        url= upload_to_s3(bucket, thumbname_key, thumbnail, image_size)
    print(url)
        
    def get_s3_image(bucket, key):
        obj = s3.get_object(Bucket=bucket, Key=key)
        return Image.open(BytesIO(obj['Body'].read()))
    
    def image_to_thumbnail(image):
        return ImageOps.fit(image, (size, size), Image.ANTIALIAS)
    
    def new_filename(key):
        key_split = key.rsplit(".",1)
        return key_split[0]+"_thumbnail.png"
    
    def upload_to_s3(bucket, key, image, image_size):
        out_thumbnail = BytesIO()
        image.save(out_thumbnail, "PNG")
        out_thumbnail.seek(0)
        response = s3.put_object(
            ACL='public-read',
            Body=out_thumbnail,
            Bucket=bucket,
            ContentType='image/png',
            key=key,
        )
        print(response)
        url='{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key)
        print(url)
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}
