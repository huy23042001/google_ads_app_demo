from typing import Optional
from google.oauth2 import id_token
from google.cloud import secretmanager
from google.auth.transport import requests
import os
import google_crc32c

_CLIENT_ID = os.getenv("CLIENT_ID")
_PROJECT_ID = os.getenv("PROJECT_ID")
_PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")

class Secret:
    def __init__(self, token):
        #get ID from token
        self.id = self.validate_token_get_id(token)
        self.client = secretmanager.SecretManagerServiceClient()
        
    def validate_token_get_id(self, token):
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), _CLIENT_ID)
            return idinfo['sub']
        except ValueError:
            # Invalid token
            pass

    def create_secret_version(self,refresh_token,ttl: Optional[str] = None):
        # Check if secret exists
        if self.does_secret_exists() is False:
            parent = f"projects/{_PROJECT_ID}"

            # Create the secret.
            self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": self.id,
                    "secret": {"replication": {"automatic": {}}, "ttl": ttl},
                }
            )

        # Create secret version unser secret
        # self.add_secret_verion(refresh_token)
        # Build the resource name of the parent secret.
        parent = self.client.secret_path(_PROJECT_ID, self.id)

        # Convert the string payload into a bytes. This step can be omitted if you
        # pass in bytes instead of a str for the payload argument.
        payload_bytes = refresh_token.encode("UTF-8")

        # Calculate payload checksum. Passing a checksum in add-version request
        # is optional.
        crc32c = google_crc32c.Checksum()
        crc32c.update(payload_bytes)

        # Add the secret version.
        self.client.add_secret_version(
            request={
                "parent": parent,
                "payload": {
                    "data": payload_bytes,
                    "data_crc32c": int(crc32c.hexdigest(), 16),
                },
            }
        )
    
    def does_secret_exists(self):
        parent = f"projects/{_PROJECT_ID}"

        # List all secret versions.
        for secret in self.client.list_secrets(request={"parent": parent}):
            secret_name = f"projects/{_PROJECT_NUMBER}/secrets/{self.id}"
            if secret.name == secret_name:
                return True
        return False
    
    # def add_secret_verion(self,refresh_token):
    #     # Build the resource name of the parent secret.
    #     parent = self.client.secret_path(_PROJECT_ID, self.id)

    #     # Convert the string payload into a bytes. This step can be omitted if you
    #     # pass in bytes instead of a str for the payload argument.
    #     payload_bytes = refresh_token.encode("UTF-8")

    #     # Calculate payload checksum. Passing a checksum in add-version request
    #     # is optional.
    #     crc32c = google_crc32c.Checksum()
    #     crc32c.update(payload_bytes)

    #     # Add the secret version.
    #     self.client.add_secret_version(
    #         request={
    #             "parent": parent,
    #             "payload": {
    #                 "data": payload_bytes,
    #                 "data_crc32c": int(crc32c.hexdigest(), 16),
    #             },
    #         }
    #     )
    
    def get_secret_version(self):
        # Build the resource name of the secret version.
        name = f"projects/{_PROJECT_ID}/secrets/{self.id}/versions/latest"

        # Access the secret version.
        response = self.client.access_secret_version(request={"name": name})

        # Verify payload checksum.
        crc32c = google_crc32c.Checksum()
        crc32c.update(response.payload.data)
        if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            print("Data corruption detected.")
            return response
        return response.payload.data.decode("UTF-8")