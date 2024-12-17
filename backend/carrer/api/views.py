import os

from rest_framework import parsers
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
from rest_framework.generics import GenericAPIView, CreateAPIView

from backend.carrer.models import Carrers
from backend.carrer.services.file_loaders import CarrerSpreadsheetUpload
from backend.carrer.api.serializers import CarrerSerializer, CarrerFileSerializer, LoginUserSerializer


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

    def post(self, request, *args, **kwargs):

        os.makedirs(f"{os.getcwd()}/media/files", exist_ok=True)
        
        file = request.data["file"]
        fs = FileSystemStorage(location=f"{os.getcwd()}/media/files")
        file = fs.save(file.name, file)

        CarrerSpreadsheetUpload(file).upload_file()
        
        fs.delete(file)
        
        return Response(
            {
                "message": "File was uploaded with success.",
            },
            status=201
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