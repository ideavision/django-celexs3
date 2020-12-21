import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import pandas as pd

import boto3
from botocore.exceptions import NoCredentialsError


class DataframeUtil(object):
    """
    This class has functions to check validation and validate excel dataframe.
    """

    @staticmethod
    def get_validated_dataframe(path: str) -> pd.DataFrame:
        '''
        Lowercases column names and fill empty values with None.

        Parameters:
        path (str): file path

        Returns:
        pd.DataFrame: validated dataframe
        '''

        df = pd.read_excel(path, dtype=str)
        df.columns = df.columns.str.lower()
        df = df.fillna(-1)
        return df.mask(df == -1, None)
    
    @staticmethod
    def is_valid_dataframe(path: str) -> bool:
        '''
        Checks if 'name', 'email' and 'phone number' exists in columns.

        Parameters:
        path (str): file path

        Returns:
        bool: validation status
        '''

        df = pd.read_excel(path, dtype=str)
        df.columns = df.columns.str.lower()
        return ('name' in df.columns) and ('email' in df.columns) and ('phone number' in df.columns)

class AWS(object):
    """
    AWS class uses boto3 package developed by amazon to upload files into aws s3 buckets.
    """

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

    @staticmethod
    def upload_file(local_file, s3_file_name):
        '''
        Uploads file into AWS S3.

        Parameters:
        local_file (str): local file path
        s3_file_name (str): destination file path on s3

        Returns:
        bool: upload status
        str: decription
        '''

        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        try:
            s3.upload_file(local_file, AWS_STORAGE_BUCKET_NAME, s3_file_name)
            return True, "AWS Upload Successful"
        except FileNotFoundError:
            return False, "The file was not found"
        except NoCredentialsError:
            return False, "AWS Credentials not available"


def in_memory_file_to_temp(in_memory_file):
    path = default_storage.save('tmp/%s' % in_memory_file.name, ContentFile(in_memory_file.read()))
    return path
