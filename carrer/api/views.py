import os
import pandas as pd

from django.db import transaction
from rest_framework import parsers
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import authenticate, login
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from carrer.models import Carrers
from carrer.api.serializers import CarrerSerializer, CarrerFileSerializer, LoginUserSerializer


class CarrerViewSet(ModelViewSet):
    queryset = Carrers.objects.all()
    serializer_class = CarrerSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("-title")

        return Response(self.get_serializer(queryset, many=True).data)

    def create(self, request, *args, **kwargs):

        request.data["title"] = request.data.get("title", None).upper()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):

        request.data["title"] = "ATUALIZADO " + request.data.get("title", None)

        return super().update(request, *args, **kwargs)


class CarrerFileUpload(GenericAPIView):
    queryset = Carrers.objects.all()
    serializer_class = CarrerFileSerializer
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.FileUploadParser,
    )

    def read_file(self, file):
        try:
            if file.name.split(".")[-1] == "xlsx":
                df = pd.read_excel(file, index_col=False)
            else:
                df = pd.read_csv(file, index_col=False)
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

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]

        data = self.read_file(file)

        with transaction.atomic():  # previne quen não sejam feitas alterações parciais no bd
            carrer_serializer = CarrerSerializer(data=data, many=True)
            carrer_serializer.is_valid(raise_exception=True)
            carrer_serializer.save()

        return Response(
            {
                "message": "File uploaded and data saved successfully.",
                "uploaded_rows": len(data),
            }
        )


class UserLogin(CreateAPIView):
    model_class = User
    serializer_class = LoginUserSerializer
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        user = authenticate(**request.data)
        
        if user:
            login(request, user)
            return Response({"message": "User Loged in"}, status=200)
        return Response({"message": "Invalid credentials"}, status=400)