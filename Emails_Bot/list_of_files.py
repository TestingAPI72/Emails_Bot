import io
import os
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload
import time

"""
This code to download mentioned file from google drive

Follow "https://youtu.be/9K2P2bWEd90?list=PL3JVwFmb_BnTamTxXbmlwpspYdpmaHdbz" for more information(from Scratch)

"""


class list_of_files:

    def __init__(self):
        print("Initializing Object")
        self.files = ['TestingJobs_Full.docx']

    def disk_cleanup(self):
        if os.path.exists(f'./Files/{self.files[0]}'):
            os.remove(f'./Files/{self.files[0]}')
            if not os.path.exists(f'./Files/{self.files[0]}'):
                print(f'{self.files[0]} Removed Successfully')
            else:
                raise IOError(f"{self.files[0]} was not removed successfully")

    def download_files_from_gmail(self):

        CLIENT_SECRET_FILE = 'client_secret_file.json'
        API_NAME = 'drive'
        API_VERSION = 'v3'

        SCOPES = ['https://www.googleapis.com/auth/drive']

        _service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

        file_ids = ['1gKh5OZETYLNsDUid4t4iX4592HjoJWxM']
        file_names = ['TestingJobs_Full.docx']

        for file_id, file_name in zip(file_ids, file_names):

            request = _service.files().get_media(fileId=file_id)

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fd=fh, request=request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print('Download Progress {0}'.format(status.progress() * 100))
            fh.seek(0)

            with open(os.path.join('./Files', file_name), 'wb') as f:
                f.write(fh.read())
                f.close()
        return True
