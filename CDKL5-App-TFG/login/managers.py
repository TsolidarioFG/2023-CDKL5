from login.constants import RolUsuario
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager): # Manager necesario para la sustitución de modelo Users por defecto en Django
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Debe especificarse un campo email')
        if not username:
            raise ValueError('Debe especificarse un campo username/nickname')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('user_role', RolUsuario.AMIGO)
        return self._create_user(username, email, password, **extra_fields)


    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('incomplete', False)
        extra_fields.setdefault('user_role', RolUsuario.ADMINISTRADOR)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener el atributo \"is_superuser\" a True.')
        return self.create_user(username, email, password, **extra_fields)

