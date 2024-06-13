# s3.py
import asyncio
from aiobotocore.session import get_session
import os
import tempfile
from pydantic import BaseModel
from typing import Type, Optional, List, Union, Dict
import json
from fastapi.encoders import jsonable_encoder
import numpy as np
import io

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')  # Replace with your desired region


async def get_files(presentationID):
   """
   Retrieve a list of files in a specific presentation folder from an S3 bucket.

   This function retrieves the list of files stored in a specific presentation folder
   within an S3 bucket. It uses the provided `presentationID` to construct the folder
   prefix and makes an asynchronous request to the S3 API using the AWS SDK for Python (Boto3).

   Args:
       presentationID (str): The ID of the presentation folder.

   Returns:
       list: A list of file names (strings) found in the specified presentation folder.
             If no files are found or an error occurs, an empty list is returned.

   Raises:
       botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
       Exception: If any other unexpected error occurs during the execution of the function.

   Example:
       files = await get_files("presentation123")
       if files:
           print("Files in the presentation folder:")
           for file in files:
               print(file)
       else:
           print("No files found in the presentation folder.")
   """
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
   """
   Delete a specific file from a presentation folder in an S3 bucket.

   This function deletes a file with the specified `filename` from the presentation folder
   identified by `presentationID` in an S3 bucket. It constructs the object key using the
   `presentationID` and `filename`, and makes an asynchronous request to the S3 API using
   the AWS SDK for Python (Boto3) to delete the object.

   Args:
       presentationID (str): The ID of the presentation folder.
       filename (str): The name of the file to be deleted.

   Returns:
       bool: True if the file is successfully deleted, False otherwise.

   Raises:
       botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
       Exception: If any other unexpected error occurs during the execution of the function.

   Example:
       result = await delete_file("presentation123", "example.txt")
       if result:
           print("File deleted successfully.")
       else:
           print("Failed to delete the file.")
   """
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
   
async def get_object(file_path):
   """
   Retrieve the contents of a file from an S3 bucket.

   This function retrieves the contents of a file specified by `file_path` from an S3 bucket.
   It makes an asynchronous request to the S3 API using the AWS SDK for Python (Boto3) to get
   the object and reads its contents.

   Args:
       file_path (str): The path of the file in the S3 bucket.

   Returns:
       bytes: The contents of the file as bytes if successfully retrieved.
       None: If an error occurs during the retrieval process.

   Raises:
       botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
       Exception: If any other unexpected error occurs during the execution of the function.

   Example:
       file_contents = await get_object("path/to/file.txt")
       if file_contents:
           print("File contents:")
           print(file_contents.decode('utf-8'))
       else:
           print("Failed to retrieve the file.")
   """
   try:
       session = get_session()
       async with session.create_client('s3', region_name=AWS_REGION,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
           bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
           response = await s3.get_object(Bucket=bucket_name, Key=file_path)
           data = await response['Body'].read()
           return data
   except Exception as e:
       print(f"Error retrieving file '{file_path}' from S3: {str(e)}")
       return None

async def download_file_to_temp(file_path):
    """
    Download a file from S3 to a temporary file.

    Args:
        file_path (str): The path of the file in the S3 bucket.

    Returns:
        tempfile.NamedTemporaryFile: The temporary file object containing the downloaded file.

    Raises:
        Exception: If an error occurs during the file download.

    Description:
        This function downloads a file from an S3 bucket to a temporary file using the provided file path.
        It creates a new session and an S3 client using the specified AWS credentials and region.
        The file is downloaded in chunks and written to a temporary file using the `tempfile.NamedTemporaryFile` function.
        The temporary file object is returned, which can be used to access the downloaded file.
        If an error occurs during the download process, an exception is raised with an error message.
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            response = await s3.get_object(Bucket=bucket_name, Key=file_path)
            async for chunk in response['Body']:
                temp_file.write(chunk)
            temp_file.seek(0)
            return temp_file
    except Exception as e:
        print(f"Error downloading file '{file_path}' from S3: {str(e)}")
        raise
   
async def upload_model_to_s3(model: BaseModel, object_key: str):
    """
    Upload a Pydantic model as JSON to an S3 bucket.

    This function serializes a Pydantic model to JSON and uploads it to an S3 bucket
    with the specified `object_key`. It makes an asynchronous request to the S3 API
    using the AWS SDK for Python (Boto3) to put the object.

    Args:
        model (BaseModel): The Pydantic model to be uploaded.
        object_key (str): The key (path) of the object in the S3 bucket.

    Returns:
        bool: True if the model is successfully uploaded, False otherwise.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
        Exception: If any other unexpected error occurs during the execution of the function.

    Example:
        my_model = MyModel(name="Example", value=42)
        result = await upload_model_to_s3(my_model, "models/example.json")
        if result:
            print("Model uploaded successfully.")
        else:
            print("Failed to upload the model.")
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            
            # Serialize the model to JSON
            model_json = model.json()
            
            # Upload the JSON data to S3
            response = await s3.put_object(Bucket=bucket_name, Key=object_key, Body=model_json)
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            
            if status_code == 200:
                print(f"Model uploaded successfully to S3 with key: {object_key}")
                return True
            else:
                print(f"Failed to upload model to S3 with key: {object_key}. Status code: {status_code}")
                return False

    except Exception as e:
        print(f"Error uploading model to S3 with key: {object_key}. Error: {str(e)}")
        return False
   
   
async def download_model_from_s3(model_class: Type[BaseModel], object_key: str) -> Optional[BaseModel]:
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            
            # Download the JSON data from S3
            response = await s3.get_object(Bucket=bucket_name, Key=object_key)
            model_json = await response['Body'].read()
            
            # Deserialize the JSON data to the BaseModel
            model = model_class.parse_raw(model_json)
            
            return model
    
    except Exception as e:
        print(f"Error downloading model from S3 with key: {object_key}. Error: {str(e)}")
        return None

async def upload_model_list_to_s3(models: List[BaseModel], object_key: str):
    """
    Upload a list of Pydantic models as a single JSON file to an S3 bucket.

    This function serializes a list of Pydantic models to a single JSON file and uploads it to an S3 bucket
    with the specified `object_key`. It makes an asynchronous request to the S3 API
    using the AWS SDK for Python (Boto3) to put the object.

    Args:
        models (List[BaseModel]): The list of Pydantic models to be uploaded.
        object_key (str): The key (path) of the object in the S3 bucket.

    Returns:
        bool: True if the models are successfully uploaded, False otherwise.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
        Exception: If any other unexpected error occurs during the execution of the function.

    Example:
        my_models = [MyModel(name="Example1", value=42), MyModel(name="Example2", value=24)]
        result = await upload_model_list_to_s3(my_models, "models/examples.json")
        if result:
            print("Models uploaded successfully.")
        else:
            print("Failed to upload the models.")
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            # Serialize the models to a JSON list
            models_json = jsonable_encoder(models)
            # Upload the JSON data to S3
            response = await s3.put_object(Bucket=bucket_name, Key=object_key, Body=json.dumps(models_json))
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            if status_code == 200:
                print(f"Models uploaded successfully to S3 with key: {object_key}")
                return True
            else:
                print(f"Failed to upload models to S3 with key: {object_key}. Status code: {status_code}")
                return False
    except Exception as e:
        print(f"Error uploading models to S3 with key: {object_key}. Error: {str(e)}")
        return False

async def download_model_list_from_s3(model_class: Type[BaseModel], object_key: str) -> Optional[List[BaseModel]]:
    """
    Downloads a list of models from an S3 bucket.

    Args:
        model_class (Type[BaseModel]): The class of the models to be downloaded.
        object_key (str): The key of the object in the S3 bucket.

    Returns:
        Optional[List[BaseModel]]: A list of downloaded models, or None if there was an error.
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            # Download the JSON data from S3
            response = await s3.get_object(Bucket=bucket_name, Key=object_key)
            models_json = await response['Body'].read()
            # Deserialize the JSON data to a list of BaseModels
            models_data = json.loads(models_json)
            models = [model_class.parse_obj(model_data) for model_data in models_data]
            return models
    except Exception as e:
        print(f"Error downloading models from S3 with key: {object_key}. Error: {str(e)}")
        return None

async def upload_data_to_s3(data: Union[List, Dict], object_key: str):
    """
    Upload a Python list or dict containing any combination of lists or dicts with strings or numbers to an S3 bucket.

    This function serializes the provided data to JSON and uploads it to an S3 bucket
    with the specified `object_key`. It makes an asynchronous request to the S3 API
    using the AWS SDK for Python (Boto3) to put the object.

    Args:
        data (Union[List, Dict]): The Python list or dict to be uploaded.
        object_key (str): The key (path) of the object in the S3 bucket.

    Returns:
        bool: True if the data is successfully uploaded, False otherwise.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
        Exception: If any other unexpected error occurs during the execution of the function.

    Example:
        my_data = {'name': 'John', 'age': 30, 'hobbies': ['reading', 'coding']}
        result = await upload_data_to_s3(my_data, "data/user.json")
        if result:
            print("Data uploaded successfully.")
        else:
            print("Failed to upload the data.")
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            
            # Serialize the data to JSON
            data_json = json.dumps(data)
            
            # Upload the JSON data to S3
            response = await s3.put_object(Bucket=bucket_name, Key=object_key, Body=data_json)
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            
            if status_code == 200:
                print(f"Data uploaded successfully to S3 with key: {object_key}")
                return True
            else:
                print(f"Failed to upload data to S3 with key: {object_key}. Status code: {status_code}")
                return False

    except Exception as e:
        print(f"Error uploading data to S3 with key: {object_key}. Error: {str(e)}")
        return False


async def download_data_from_s3(object_key: str) -> Optional[Union[List, Dict]]:
    """
    Download a Python list or dict containing any combination of lists or dicts with strings or numbers from an S3 bucket.

    This function downloads the JSON data from an S3 bucket with the specified `object_key`
    and deserializes it into a Python list or dict. It makes an asynchronous request to the S3 API
    using the AWS SDK for Python (Boto3) to get the object.

    Args:
        object_key (str): The key (path) of the object in the S3 bucket.

    Returns:
        Optional[Union[List, Dict]]: The downloaded Python list or dict if successful, None otherwise.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
        Exception: If any other unexpected error occurs during the execution of the function.

    Example:
        data = await download_data_from_s3("data/user.json")
        if data:
            print("Downloaded data:", data)
        else:
            print("Failed to download the data.")
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            
            # Download the JSON data from S3
            response = await s3.get_object(Bucket=bucket_name, Key=object_key)
            data_json = await response['Body'].read()
            
            # Deserialize the JSON data to a Python list or dict
            data = json.loads(data_json)
            
            return data
    
    except Exception as e:
        print(f"Error downloading data from S3 with key: {object_key}. Error: {str(e)}")
        return None


async def upload_np_array_to_s3(array: np.ndarray, object_key: str):
    """
    Upload a NumPy array to an S3 bucket as a .npy file.

    This function saves the provided NumPy array as a .npy file and uploads it to an S3 bucket
    with the specified `object_key`. It makes an asynchronous request to the S3 API
    using the AWS SDK for Python (Boto3) to put the object.

    Args:
        array (np.ndarray): The NumPy array to be uploaded.
        object_key (str): The key (path) of the object in the S3 bucket.

    Returns:
        bool: True if the array is successfully uploaded, False otherwise.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
        Exception: If any other unexpected error occurs during the execution of the function.

    Example:
        my_array = np.array([[1, 2, 3], [4, 5, 6]])
        result = await upload_np_array_to_s3(my_array, "data/array.npy")
        if result:
            print("Array uploaded successfully.")
        else:
            print("Failed to upload the array.")
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            
            # Save the NumPy array as a .npy file
            with io.BytesIO() as buffer:
                np.save(buffer, array)
                buffer.seek(0)
                
                # Upload the .npy file to S3
                response = await s3.put_object(Bucket=bucket_name, Key=object_key, Body=buffer)
                status_code = response['ResponseMetadata']['HTTPStatusCode']
                
                if status_code == 200:
                    print(f"Array uploaded successfully to S3 with key: {object_key}")
                    return True
                else:
                    print(f"Failed to upload array to S3 with key: {object_key}. Status code: {status_code}")
                    return False

    except Exception as e:
        print(f"Error uploading array to S3 with key: {object_key}. Error: {str(e)}")
        return False


async def download_np_array_from_s3(object_key: str) -> Optional[np.ndarray]:
    """
    Download a NumPy array from an S3 bucket stored as a .npy file.

    This function downloads the .npy file from an S3 bucket with the specified `object_key`
    and loads it into a NumPy array. It makes an asynchronous request to the S3 API
    using the AWS SDK for Python (Boto3) to get the object.

    Args:
        object_key (str): The key (path) of the object in the S3 bucket.

    Returns:
        Optional[np.ndarray]: The downloaded NumPy array if successful, None otherwise.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
        Exception: If any other unexpected error occurs during the execution of the function.

    Example:
        array = await download_np_array_from_s3("data/array.npy")
        if array is not None:
            print("Downloaded array:", array)
        else:
            print("Failed to download the array.")
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            
            # Download the .npy file from S3
            response = await s3.get_object(Bucket=bucket_name, Key=object_key)
            data = await response['Body'].read()
            
            # Load the .npy file into a NumPy array
            with io.BytesIO(data) as buffer:
                array = np.load(buffer)
            
            return array
    
    except Exception as e:
        print(f"Error downloading array from S3 with key: {object_key}. Error: {str(e)}")
        return None
    
async def upload_bytes_to_s3(data: bytes, object_key: str):
    """
    Upload bytes to a file in an S3 bucket.

    This function uploads the provided bytes to a file in an S3 bucket
    with the specified `object_key`. It makes an asynchronous request to the S3 API
    using the AWS SDK for Python (Boto3) to put the object.

    Args:
        data (bytes): The bytes to be uploaded.
        object_key (str): The key (path) of the object in the S3 bucket.

    Returns:
        bool: True if the bytes are successfully uploaded, False otherwise.

    Raises:
        botocore.exceptions.ClientError: If an error occurs while communicating with the S3 API.
        Exception: If any other unexpected error occurs during the execution of the function.

    Example:
        my_bytes = b'Hello, World!'
        result = await upload_bytes_to_s3(my_bytes, "data/file.txt")
        if result:
            print("Bytes uploaded successfully.")
        else:
            print("Failed to upload the bytes.")
    """
    try:
        session = get_session()
        async with session.create_client('s3', region_name=AWS_REGION,
                                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                         aws_access_key_id=AWS_ACCESS_KEY_ID) as s3:
            bucket_name = os.environ.get('SOURCES_BUCKET_NAME')
            
            # Upload the bytes to S3
            response = await s3.put_object(Bucket=bucket_name, Key=object_key, Body=data)
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            
            if status_code == 200:
                print(f"Bytes uploaded successfully to S3 with key: {object_key}")
                return True
            else:
                print(f"Failed to upload bytes to S3 with key: {object_key}. Status code: {status_code}")
                return False

    except Exception as e:
        print(f"Error uploading bytes to S3 with key: {object_key}. Error: {str(e)}")
        return False


class User(BaseModel):
   name: str
   age: int
   email: str
   
   

async def main():
   presentationID = "example_presentation"
   files = await get_files(presentationID)
   print(f"Files in {presentationID} folder: {files}")

   filename = "example_file.txt"
   result = await delete_file(presentationID, filename)
   print(f"Deletion of file '{filename}' from {presentationID} folder: {result}")
   
   # Create a User model instance
   user = User(name="John Doe", age=25, email="john@example.com")
   
   # Upload the User model to S3
   object_key = f"{presentationID}/user.json"
   upload_result = await upload_model_to_s3(user, object_key)
   print(f"Upload of User model to S3 with key '{object_key}': {upload_result}")

if __name__ == "__main__":
   asyncio.run(main())