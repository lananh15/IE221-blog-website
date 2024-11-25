from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from .models import User

@receiver(user_logged_in)
def google_login_handler(sender, request, user, **kwargs):
    try:
        social_account = SocialAccount.objects.get(user=user, provider='google')
        extra_data = social_account.extra_data

        google_id = extra_data.get('sub')
        full_name = extra_data.get('name')
        avatar = extra_data.get('picture')
        email = extra_data.get('email')

        # print(f"Google ID: {google_id}")
        # print(f"Full Name: {full_name}")
        # print(f"Avatar: {avatar}")
        # print(f"Email: {email}")

        if not User.objects.filter(email=email).exists():
            new_user = User.objects.create(
                name=full_name,
                email=email,
                password='',
            )
            print(f"New user created with email: {email}")
            user = User.objects.get(email=email)
            request.session['user_id'] = user.id

        else:
            existing_user = User.objects.get(email=email)
            user_id = existing_user.id
            user_name = existing_user.name
            print(f"Existing user found: ID = {user_id}, Name = {user_name}")
            request.session['user_id'] = existing_user.id

    except SocialAccount.DoesNotExist:
        print("User does not have a linked Google account.")