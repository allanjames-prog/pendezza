from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save

import uuid
from django.db import models

GENDER = (
  ("Female", "Female"),
  ("Male", "Male"),
  ("Other", "Other"),
)

IDENTITY_TYPE = (
  ("National Identification Number", "National Identification Number"),
  ("Driver's Licence", "river's Licence"),
  ("International Passport", "International Passport"),
)

def user_directory_path(instance, filename):
  # Extract the file extension from the original filename
  ext = filename.split(".")[-1]
   # Rename the file using the user's ID and append the original filename
  filename = "%s.%s" %(instance.user.id, filename)
  return "user_{0}/{1}".format(instance.user.id, filename)
  


class User(AbstractUser):
  full_name = models.CharField(max_length=200, null=True, blank=True)
  username = models.CharField(max_length=200, unique=True)
  email = models.EmailField(unique=True)
  phone = models.CharField(max_length=50, null=True)
  gender = models.CharField(max_length=20, choices=GENDER, default="Other")
  otp = models.CharField(max_length=100, null=True, blank=True)

  # Fix for the reverse accessor clashes
  groups = models.ManyToManyField(Group, related_name='%(app_label)s_%(class)s_groups', related_query_name='%(app_label)s_%(class)s', blank=True,)

  user_permissions = models.ManyToManyField(Permission, related_name='%(app_label)s_%(class)s_permissions', related_query_name='%(app_label)s_%(class)s', blank=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']

  def __str__(self):
    return self.full_name or self.email or str(self.pk)  # Fallback to email or ID
  
def generate_short_uuid():
  """Generates a 25-character UUID"""
  return str(uuid.uuid4())[:25]

class Profile(models.Model):
  profile_id = models.CharField(max_length=25, default=generate_short_uuid, unique=True,editable=False)
  image = models.FileField(upload_to=user_directory_path, default="default.jpg", null=True, blank=True)
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  full_name = models.CharField(max_length=200, null=True, blank=True)
  phone = models.CharField(max_length=50, null=True, blank=True)
  gender = models.CharField(max_length=20, choices=GENDER, default="Other")

  country = models.CharField(max_length=100, null=True, blank=True)
  city = models.CharField(max_length=100, null=True, blank=True)
  state = models.CharField(max_length=100, null=True, blank=True)
  address = models.CharField(max_length=500, null=True, blank=True)

  identity_type = models.CharField(max_length=100, choices=IDENTITY_TYPE, null=True, blank=True)
  identity_image = models.FileField(upload_to=user_directory_path, default="default.jpg", null=True, blank=True) 

  linkedin = models.URLField(max_length=100, null=True, blank=True) 
  twitter = models.URLField(max_length=100, null=True, blank=True) 

  wallet = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
  verified = models.BooleanField(default=False)
  

  date = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-date']

  def __str__(self):
    if self.full_name:
      return f"{self.full_name}"
    else:
      return f"{self.user.username}"
  

def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)







