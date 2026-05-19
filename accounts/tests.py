from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


User = get_user_model()


# ===========================
# MODEL TESTS
# ===========================

class CustomUserModelTest(TestCase):
    """Tests for the CustomUser model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )

    def test_user_creation(self):
        """Test user is created with correct credentials"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@email.com")

    def test_user_email_unique(self):
        """Test that email must be unique"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="anotheruser",
                email="test@email.com",
                password="secret123",
            )

    def test_user_password_hash(self):
        """Test that password is hashed"""
        self.assertNotEqual(self.user.password, "secret123")
        self.assertTrue(self.user.check_password("secret123"))

    def test_user_string_representation(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), "testuser")

    def test_user_with_name_field(self):
        """Test user can have name field"""
        user = User.objects.create_user(
            username="nameduser",
            email="named@email.com",
            password="secret123",
            name="John Doe"
        )
        self.assertEqual(user.name, "John Doe")

    def test_superuser_creation(self):
        """Test superuser creation"""
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@email.com",
            password="secret123",
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


# ===========================
# VIEW TESTS
# ===========================

class UserMeAPITest(APITestCase):
    """Tests for the UserMe view"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@email.com",
            password="secret123",
        )
        self.url = reverse('user_me')

    def test_user_me_authenticated(self):
        """Test authenticated user can access their own data"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "testuser")
        self.assertEqual(response.data['email'], "test@email.com")

    def test_user_me_unauthenticated(self):
        """Test unauthenticated users cannot access /me endpoint"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_me_returns_own_data(self):
        """Test user only sees their own data, not others"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertNotEqual(response.data['username'], self.other_user.username)

    def test_user_me_has_expected_fields(self):
        """Test /me endpoint returns expected user fields"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)


class UserViewSetAPITest(APITestCase):
    """Tests for the UserViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@email.com",
            password="secret123",
        )
        self.regular_user = User.objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@email.com",
            password="secret123",
        )
        self.url = reverse('users-list')

    def test_list_users_admin(self):
        """Test admin users can list all users"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # admin + 2 regular users

    def test_list_users_non_admin(self):
        """Test non-admin users cannot list users"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_unauthenticated(self):
        """Test unauthenticated users cannot list users"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_admin(self):
        """Test admin users can retrieve a specific user"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('users-detail', kwargs={'pk': self.regular_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "testuser")

    def test_retrieve_user_non_admin(self):
        """Test non-admin users cannot retrieve specific user"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('users-detail', kwargs={'pk': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_admin(self):
        """Test admin users can create users"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'username': 'newuser',
            'email': 'newuser@email.com',
            'password': 'secret123',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')

    def test_create_user_non_admin(self):
        """Test non-admin users cannot create users"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'username': 'newuser',
            'email': 'newuser@email.com',
            'password': 'secret123',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_admin(self):
        """Test admin users can update users"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('users-detail', kwargs={'pk': self.regular_user.id})
        data = {'username': 'updateduser'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.username, 'updateduser')

    def test_update_user_non_admin(self):
        """Test non-admin users cannot update users"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('users-detail', kwargs={'pk': self.other_user.id})
        data = {'username': 'hackeduser'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_admin(self):
        """Test admin users can delete users"""
        self.client.force_authenticate(user=self.admin_user)
        user_to_delete = User.objects.create_user(
            username="deleteuser",
            email="delete@email.com",
            password="secret123",
        )
        url = reverse('users-detail', kwargs={'pk': user_to_delete.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user_to_delete.id).exists())

    def test_delete_user_non_admin(self):
        """Test non-admin users cannot delete users"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('users-detail', kwargs={'pk': self.other_user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
