import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import IronMeasurement, SoilMoisture
from django.utils import timezone
from datetime import datetime

class OceanAnalyticsTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create some test data
        self.iron_measurement = IronMeasurement.objects.create(
            cruise='TEST001',
            datetime=timezone.now(),
            lat=45.0,
            lon=-122.0,
            depth=100.0,
            dfe=0.5,
            rrs_443=0.008
        )
        
        self.soil_moisture = SoilMoisture.objects.create(
            datetime=timezone.now(),
            site='TEST_SITE',
            soil_moisture=0.35,
            sensorZ=10.0
        )
        
        # Set up the test client
        self.client = Client()

    def test_home_page_loads(self):
        """Test that home page loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/home.html')

    def test_login_required_for_data_pages(self):
        """Test that data pages require login"""
        # Try accessing pages without login
        iron_response = self.client.get(reverse('dissolved_iron'))
        soil_response = self.client.get(reverse('soil_moisture'))
        
        # Should redirect to login page
        self.assertEqual(iron_response.status_code, 302)
        self.assertEqual(soil_response.status_code, 302)
        
        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        
        iron_response = self.client.get(reverse('dissolved_iron'))
        soil_response = self.client.get(reverse('soil_moisture'))
        
        self.assertEqual(iron_response.status_code, 200)
        self.assertEqual(soil_response.status_code, 200)

    def test_data_display(self):
        """Test that data is correctly displayed"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('dissolved_iron'))
        self.assertContains(response, 'TEST001')  # Check cruise name appears
        self.assertContains(response, '45.0')     # Check latitude appears
        
        response = self.client.get(reverse('soil_moisture'))
        self.assertContains(response, 'TEST_SITE')

    def test_signup_functionality(self):
        """Test user signup process"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        })
        
        # Should redirect after successful signup
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
