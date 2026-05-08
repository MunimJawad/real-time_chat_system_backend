from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class ProfileAPITestCase(APITestCase):

    def setUp(self):
        # Create user (profile auto-created via signal)
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )

        # Use auto-created profile
        self.profile = self.user.profile
        self.profile.full_name = "Test User"
        self.profile.bio = "This is a bio"
        self.profile.date_of_birth = "1990-01-01"
        self.profile.save()

        # JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Endpoint
        self.url = f"/accounts/v1/profile/{self.profile.id}/"

    def test_get_profile_success(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile"]["full_name"], "Test User")
        self.assertEqual(response.data["profile"]["bio"], "This is a bio")
        self.assertEqual(response.data["profile"]["date_of_birth"], "1990-01-01")

    def test_get_profile_other_user_allowed(self):
        # Another user can view profile
        another_user = User.objects.create_user(
            username="anotheruser",
            email="anotheruser@example.com",
            password="anotherpassword"
        )

        refresh = RefreshToken.for_user(another_user)
        token = str(refresh.access_token)

        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("profile", response.data)

    def test_put_profile_success(self):
        updated_data = {
            "bio": "Updated bio",
            "date_of_birth": "1991-01-01",
            "workplace": "TechCorp"
        }

        response = self.client.put(
            self.url,
            updated_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Updated bio")
        self.assertEqual(str(self.profile.date_of_birth), "1991-01-01")
        self.assertEqual(self.profile.workplace, "TechCorp")

    def test_put_profile_unauthorized(self):
        # Another user cannot edit
        another_user = User.objects.create_user(
            username="anotheruser",
            email="anotheruser@example.com",
            password="anotherpassword"
        )

        refresh = RefreshToken.for_user(another_user)
        token = str(refresh.access_token)

        updated_data = {
            "bio": "Hacked bio"
        }

        response = self.client.put(
            self.url,
            updated_data,
            HTTP_AUTHORIZATION=f"Bearer {token}",
            content_type="application/json"
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
        self.assertIn("error", response.data)

    def test_put_profile_empty_bio_allowed(self):
        # Empty bio is allowed
        data = {
            "bio": "",
            "date_of_birth": "1990-01-01"
        }

        response = self.client.put(
            self.url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "")