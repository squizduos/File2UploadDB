import random
import string

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_regular_user(self, username, email, **extra_fields):
        """
        Creates and saves a User with the given email. Can't login until password is set
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_unusable_password()
        user.login_hash = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
        user.save(using=self._db)
        return user

    def _create_admin_user(self, username, email, password, **extra_fields):
        """
        Creates and saves an admin User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_regular_user(username, email, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_admin_user(username, email, password, **extra_fields)
