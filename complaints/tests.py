from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Complaint, Comments, Category
from .permissions import IsAuthororReadOnly, IsAdminOrReadOnly


# ===========================
# MODEL TESTS
# ===========================

class CategoryModelTest(TestCase):
    """Tests for the Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="IT Support")
    
    def test_category_creation(self):
        """Test category is created with correct name"""
        self.assertEqual(self.category.name, "IT Support")
    
    def test_category_string_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), "IT Support")
    
    def test_category_unique_constraint(self):
        """Test that category names must be unique"""
        with self.assertRaises(Exception):
            Category.objects.create(name="IT Support")


class ComplaintModelTest(TestCase):
    """Tests for the Complaint model"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        cls.category = Category.objects.create(name="IT Support")
        cls.complaint = Complaint.objects.create(
            created_by=cls.user,
            title="A complaint of somekind",
            body="SOMETHING SOMETHING SOMETHING SOMETHING COMPLAIN",
            category=cls.category,
            status=Complaint.Status.SUBMITTED,
        )

    def test_complaint_creation(self):
        """Test complaint is created with correct data"""
        self.assertEqual(self.complaint.created_by.username, "testuser")
        self.assertEqual(self.complaint.title, "A complaint of somekind")
        self.assertEqual(self.complaint.body, "SOMETHING SOMETHING SOMETHING SOMETHING COMPLAIN")
        self.assertEqual(self.complaint.category.name, "IT Support")
        self.assertEqual(self.complaint.status, Complaint.Status.SUBMITTED)

    def test_complaint_string_representation(self):
        """Test complaint string representation"""
        self.assertEqual(str(self.complaint), "A complaint of somekind")

    def test_complaint_default_priority(self):
        """Test complaint has default priority of LOW"""
        self.assertEqual(self.complaint.priority, Complaint.Priority.LOW)

    def test_complaint_status_choices(self):
        """Test complaint status choices are valid"""
        valid_statuses = [
            Complaint.Status.SUBMITTED,
            Complaint.Status.IN_PROGRESS,
            Complaint.Status.RESOLVED,
            Complaint.Status.REJECTED,
        ]
        for status_choice in valid_statuses:
            complaint = Complaint.objects.create(
                created_by=self.user,
                title=f"Test {status_choice}",
                body="Test body",
                status=status_choice,
            )
            self.assertEqual(complaint.status, status_choice)

    def test_complaint_priority_choices(self):
        """Test complaint priority choices are valid"""
        valid_priorities = [
            Complaint.Priority.LOW,
            Complaint.Priority.MEDIUM,
            Complaint.Priority.HIGH,
        ]
        for priority_choice in valid_priorities:
            complaint = Complaint.objects.create(
                created_by=self.user,
                title=f"Test {priority_choice}",
                body="Test body",
                priority=priority_choice,
            )
            self.assertEqual(complaint.priority, priority_choice)

    def test_complaint_timestamps(self):
        """Test complaint has correct timestamps"""
        self.assertIsNotNone(self.complaint.created_at)
        self.assertIsNotNone(self.complaint.updated_at)


class CommentsModelTest(TestCase):
    """Tests for the Comments model"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        cls.category = Category.objects.create(name="IT Support")
        cls.complaint = Complaint.objects.create(
            created_by=cls.user,
            title="Test Complaint",
            body="Test body",
            category=cls.category,
        )
        cls.comment = Comments.objects.create(
            complaint=cls.complaint,
            comment_body="We are looking into this.",
            comment_author=cls.user,
        )

    def test_comment_creation(self):
        """Test comment is created with correct data"""
        self.assertEqual(self.comment.comment_body, "We are looking into this.")
        self.assertEqual(self.comment.comment_author.username, "testuser")
        self.assertEqual(self.comment.complaint, self.complaint)

    def test_comment_string_representation(self):
        """Test comment string representation"""
        expected = f"Comment by testuser on '{self.complaint.title}'"
        self.assertEqual(str(self.comment), expected)

    def test_comment_has_created_at(self):
        """Test comment has created_at timestamp"""
        self.assertIsNotNone(self.comment.created_at)

    def test_comment_cascade_delete(self):
        """Test comments are deleted when complaint is deleted"""
        comment_id = self.comment.id
        self.complaint.delete()
        self.assertFalse(Comments.objects.filter(id=comment_id).exists())


# ===========================
# SERIALIZER TESTS
# ===========================

class ComplaintSerializerTest(TestCase):
    """Tests for the Complaint serializer"""
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="IT Support")

    def test_complaint_serializer_has_expected_fields(self):
        """Test complaint serializer has all expected fields"""
        from .serializers import ComplaintSerializer
        complaint = Complaint.objects.create(
            created_by=self.user,
            title="Test",
            body="Test body",
            category=self.category,
        )
        serializer = ComplaintSerializer(complaint)
        self.assertEqual(set(serializer.data.keys()), {
            'id', 'title', 'body', 'created_by', 'created_at',
            'updated_at', 'category', 'category_name', 'priority', 'status'
        })

    def test_complaint_serializer_category_name_field(self):
        """Test complaint serializer includes category name"""
        from .serializers import ComplaintSerializer
        complaint = Complaint.objects.create(
            created_by=self.user,
            title="Test",
            body="Test body",
            category=self.category,
        )
        serializer = ComplaintSerializer(complaint)
        self.assertEqual(serializer.data['category_name'], "IT Support")


# ===========================
# VIEW TESTS - AUTHENTICATION & PERMISSIONS
# ===========================

class ComplaintListAPITest(APITestCase):
    """Tests for the ComplaintList view"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="other@email.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="IT Support")
        self.complaint = Complaint.objects.create(
            created_by=self.user,
            title="Test Complaint",
            body="Test body",
            category=self.category,
        )
        self.url = reverse('complaint_list')

    def test_list_complaints_unauthenticated(self):
        """Test unauthenticated users can list complaints"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_complaint_authenticated(self):
        """Test authenticated users can create complaints"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Complaint',
            'body': 'New body',
            'category': self.category.id,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_by'], self.user.username)

    def test_create_complaint_unauthenticated(self):
        """Test unauthenticated users cannot create complaints"""
        data = {
            'title': 'New Complaint',
            'body': 'New body',
            'category': self.category.id,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_complaint_sets_created_by(self):
        """Test created_by is automatically set to the authenticated user"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Complaint',
            'body': 'New body',
            'category': self.category.id,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.data['created_by'], self.user.username)
        # Verify it's not set to other_user even if we try
        self.assertNotEqual(response.data['created_by'], self.other_user.username)


class ComplaintDetailAPITest(APITestCase):
    """Tests for the ComplaintDetail view"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="other@email.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="IT Support")
        self.complaint = Complaint.objects.create(
            created_by=self.user,
            title="Test Complaint",
            body="Test body",
            category=self.category,
        )
        self.url = reverse('complaint_list_id', kwargs={'pk': self.complaint.id})

    def test_retrieve_complaint_unauthenticated(self):
        """Test unauthenticated users can retrieve complaint"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_complaint_by_author(self):
        """Test complaint author can update their complaint"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Title', 'body': 'Updated body'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_update_complaint_by_non_author(self):
        """Test non-author cannot update complaint"""
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'Updated Title', 'body': 'Updated body'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_complaint_by_author(self):
        """Test complaint author can delete their complaint"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_complaint_by_non_author(self):
        """Test non-author cannot delete complaint"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_complaint_unauthenticated(self):
        """Test unauthenticated user cannot delete complaint"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentsListCreateAPITest(APITestCase):
    """Tests for the CommentsListCreate view"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="other@email.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="IT Support")
        self.complaint = Complaint.objects.create(
            created_by=self.user,
            title="Test Complaint",
            body="Test body",
            category=self.category,
        )
        self.url = reverse('comment_list', kwargs={'complaint_id': self.complaint.id})

    def test_list_comments_unauthenticated(self):
        """Test unauthenticated users can list comments"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment_authenticated(self):
        """Test authenticated users can create comments"""
        self.client.force_authenticate(user=self.user)
        data = {'comment_body': 'This is a comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_author'], self.user.username)

    def test_create_comment_unauthenticated(self):
        """Test unauthenticated users cannot create comments"""
        data = {'comment_body': 'This is a comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_sets_comment_author(self):
        """Test comment_author is automatically set to authenticated user"""
        self.client.force_authenticate(user=self.user)
        data = {'comment_body': 'This is a comment'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.data['comment_author'], self.user.username)

    def test_comments_filtered_by_complaint(self):
        """Test comments are filtered by complaint_id"""
        comment = Comments.objects.create(
            complaint=self.complaint,
            comment_body="Test comment",
            comment_author=self.user,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], comment.id)


class CommentsDetailAPITest(APITestCase):
    """Tests for the CommentsDetail view"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="other@email.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="IT Support")
        self.complaint = Complaint.objects.create(
            created_by=self.user,
            title="Test Complaint",
            body="Test body",
            category=self.category,
        )
        self.comment = Comments.objects.create(
            complaint=self.complaint,
            comment_body="Test comment",
            comment_author=self.user,
        )
        self.url = reverse('comments_detail', kwargs={'pk': self.comment.id})

    def test_update_comment_by_author(self):
        """Test comment author can update their comment"""
        self.client.force_authenticate(user=self.user)
        data = {'comment_body': 'Updated comment'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment_by_non_author(self):
        """Test non-author cannot update comment"""
        self.client.force_authenticate(user=self.other_user)
        data = {'comment_body': 'Updated comment'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_by_author(self):
        """Test comment author can delete their comment"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_by_non_author(self):
        """Test non-author cannot delete comment"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CategoryListAPITest(APITestCase):
    """Tests for the CategoryList view"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@email.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="IT Support")
        self.url = reverse('category_list')

    def test_list_categories_unauthenticated(self):
        """Test unauthenticated users can list categories"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_admin(self):
        """Test admin users can create categories"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'New Category'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_non_admin(self):
        """Test non-admin users cannot create categories"""
        self.client.force_authenticate(user=self.user)
        data = {'name': 'New Category'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_unauthenticated(self):
        """Test unauthenticated users cannot create categories"""
        data = {'name': 'New Category'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ComplaintListByCategoryAPITest(APITestCase):
    """Tests for the ComplaintListByCategory view"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.category1 = Category.objects.create(name="IT Support")
        self.category2 = Category.objects.create(name="HR")
        
        self.complaint1 = Complaint.objects.create(
            created_by=self.user,
            title="IT Complaint",
            body="IT issue",
            category=self.category1,
        )
        self.complaint2 = Complaint.objects.create(
            created_by=self.user,
            title="HR Complaint",
            body="HR issue",
            category=self.category2,
        )

    def test_list_complaints_by_category(self):
        """Test complaints are filtered by category"""
        url = reverse('complaint_by_category', kwargs={'category_id': self.category1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.complaint1.id)

    def test_list_complaints_by_different_category(self):
        """Test complaints are correctly filtered for different categories"""
        url = reverse('complaint_by_category', kwargs={'category_id': self.category2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.complaint2.id)


class ComplaintListUserAPITest(APITestCase):
    """Tests for the ComplaintListUser view"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@email.com",
            password="secret123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="other@email.com",
            password="secret123",
        )
        self.category = Category.objects.create(name="IT Support")
        
        self.complaint1 = Complaint.objects.create(
            created_by=self.user,
            title="My Complaint",
            body="My issue",
            category=self.category,
        )
        self.complaint2 = Complaint.objects.create(
            created_by=self.other_user,
            title="Other Complaint",
            body="Other issue",
            category=self.category,
        )
        self.url = reverse('complaint_list_user')

    def test_list_user_complaints_authenticated(self):
        """Test authenticated users can see only their complaints"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.complaint1.id)

    def test_list_other_user_complaints(self):
        """Test users only see their own complaints"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.complaint2.id)

    def test_list_user_complaints_unauthenticated(self):
        """Test unauthenticated users cannot access their complaints"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)