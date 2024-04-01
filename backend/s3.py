import asyncio
from aiobotocore.session import get_session
import os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')  # Replace with your desired region

async def get_files(presentationID):
    prefix = f"{presentationID}/"
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            response = await s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    file_key = obj['Key']
                    if file_key != prefix:  # Exclude the folder itself from the list
                        file_name = file_key.replace(prefix, '')  # Remove the folder prefix
                        files.append(file_name)
            return files
    except Exception as e:
        print(f"Error listing files in {presentationID} folder: {str(e)}")
        return []

async def delete_file(presentationID, filename):
    object_key = f"{presentationID}/{filename}"
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            response = await s3.delete_object(Bucket=bucket_name, Key=object_key)
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            if status_code == 204:
                print(f"File '{filename}' deleted successfully from {presentationID} folder.")
                return True
            else:
                print(f"Failed to delete file '{filename}' from {presentationID} folder. Status code: {status_code}")
                return False
    except Exception as e:
        print(f"Error deleting file '{filename}' from {presentationID} folder: {str(e)}")
        return False

async def main():
    presentationID = "example_presentation"
    files = await get_files(presentationID)
    print(f"Files in {presentationID} folder: {files}")

    filename = "example_file.txt"
    result = await delete_file(presentationID, filename)
    print(f"Deletion of file '{filename}' from {presentationID} folder: {result}")

if __name__ == "__main__":
    asyncio.run(main())