import os

import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError

from backend.carrer.api.serializers import CarrerSerializer

class CarrerSpreadsheetUpload:
    def __init__(self, file) -> None:
        self.file = f"{os.getcwd()}/media/files/{file}"
    
    def read_file(self):
        try:
            if self.file.split(".")[-1] == "xlsx":
                df = pd.read_excel(self.file, index_col=False)
            else:
                df = pd.read_csv(self.file, index_col=False)
        except Exception as e:
            raise ValidationError(f"Error reading file: {str(e)}")

        required_columns = {"username", "title", "content"}
        if not required_columns.issubset(df.columns):
            raise ValidationError(
                "The file must contain the columns: username, title, and content."
            )

        data = [
            {
                "username": row[1]["username"],
                "title": row[1]["title"],
                "content": row[1]["content"],
            }
            for row in df.iterrows()
        ]

        return data

    def handle_file(self):
        try:
            data = self.read_file()
        
            with transaction.atomic():  # previne quen não sejam feitas alterações parciais no bd
                carrer_serializer = CarrerSerializer(data=data, many=True)
                carrer_serializer.is_valid(raise_exception=True)
                carrer_serializer.save()
            
            return True

        except Exception as e:
            raise ValidationError(f"Error handling file: {str(e)}")


    def upload_file(self):
        self.handle_file()