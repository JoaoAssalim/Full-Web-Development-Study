from .models import Carrers
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from backend.carrer.api.serializers import CarrerSerializer

class CarrerViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.career1 = Carrers.objects.create(username="Joao", title="Engenharia", content="Engenharia de Software")
        self.career2 = Carrers.objects.create(username="Jose", title="Programador", content="Programador Python")
        
        self.list_url = reverse('carrer-list')

    def test_list_careers(self):
        response = self.client.get(self.list_url)
        careers = Carrers.objects.all()
        serializer = CarrerSerializer(careers, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_career(self):
        data = {"username": "Joao", "title": "Arquitetura", "content": "Arquitetura de Software"}
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Carrers.objects.count(), 3)
        self.assertEqual(Carrers.objects.get(id=response.data['id']).title, 'Arquitetura')

    def test_update_career(self):
        update_url = reverse('carrer-detail', args=[self.career1.id])
        data = {'title': 'Engenharia Atualizada'}
        response = self.client.patch(update_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.career1.refresh_from_db()
        self.assertEqual(self.career1.title, 'Engenharia Atualizada')

    def test_delete_career(self):
        delete_url = reverse('carrer-detail', args=[self.career1.id])
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Carrers.objects.count(), 1)
