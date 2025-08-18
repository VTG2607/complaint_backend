from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Complaint, Comments,Category


class ComplaintTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username= "testuser2",
            email="test@email.com",
            password="secret",
        )

        cls.category = Category.objects.create(name="IT Support")

        cls.complaint = Complaint.objects.create(
            created_by = cls.user,
            title = "A complaint of somekind",
            body = "SOMETHING SOMETHING SOMETHING SOMETHING COMPLAIN",
            category = cls.category,
            status = Complaint.Status.SUBMITTED,
        )


    def test_post_model(self):
        self.assertEqual(self.complaint.created_by.username, "testuser2")
        self.assertEqual(self.complaint.title, "A complaint of somekind")
        self.assertEqual(self.complaint.body, "SOMETHING SOMETHING SOMETHING SOMETHING COMPLAIN")
        self.assertEqual(str(self.complaint), "A complaint of somekind")


    def test_setUp_comment(self):
        comment = Comments.objects.create(
            post=self.complaint,
            comment_body="We are looking into this.",
            comment_author=self.user,
        )
        self.assertEqual(comment.comment_body, "We are looking into this.")
        self.assertEqual(comment.comment_author.username, "testuser2")
        self.assertEqual(comment.post, self.complaint)