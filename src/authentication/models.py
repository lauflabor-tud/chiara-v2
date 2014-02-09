from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from utils.enums import Permission


class UserManager(BaseUserManager):
    """Manager for the User model. It is responsible for creating users.
    The manager inherit from the django user manager."""
    
    def create_user(self, user_name, first_name, last_name, email, password=None):
        """Creates and saves a User with the given user, first and last name, email
        and password"""
        if not user_name:
            raise ValueError('Users must have a user name')
        if not first_name:
            raise ValueError('Users must have a first name')
        if not last_name:
            raise ValueError('Users must have a last name')
        if not email:
            raise ValueError('Users must have an email address')
        
        user = self.model(user_name=user_name,
                          first_name=first_name,
                          last_name=last_name,
                          email=email,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, first_name, last_name, email, password):
        """Creates and saves a superuser with the given user, first and last name, email
        and password"""
        user = self.create_user(user_name=user_name,
                                password=password,
                                first_name=first_name,
                                last_name=last_name,
                                email=email)
        
        user.is_admin = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser):
    """The User model manages the users of chiara. All their information will be saved
    in this model.
    The user inherit from the django user."""
    
    user_name = models.CharField(verbose_name=u'user name', max_length=30, unique=True)
    first_name = models.CharField(verbose_name=u'first name', max_length=30)
    last_name = models.CharField(verbose_name=u'last name', max_length=30)
    email = models.EmailField(verbose_name=u'email address', max_length=120, unique=True)
    
    is_active = models.BooleanField(verbose_name=u'is active', default=True)
    is_admin = models.BooleanField(verbose_name=u'is admin', default=False)
    
    permissions = models.ManyToManyField('collection.Collection', 
                                         blank=True,
                                         related_name='permissible_users', 
                                         through='authentication.UserPermission')
    subscriptions = models.ManyToManyField('collection.Collection',
                                           blank=True,
                                           related_name='users_who_subscribed',
                                           through='authentication.Subscription')

    objects = UserManager()

    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def get_full_name(self):
        return self.user_name

    def get_short_name(self):
        return self.user_name

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_admin

    def __unicode__(self):
        return self.user_name
    
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
    
    
    
class Group(models.Model):
    """The Group model manages the groups of chiara."""
    
    group_name = models.CharField(verbose_name=u'group name', max_length=50, unique=True)
    users = models.ManyToManyField('authentication.User',
                                   blank=True,
                                   related_name='groups',
                                   through='authentication.Membership')
    permissions = models.ManyToManyField('collection.Collection',
                                         blank=True,
                                         related_name='permissible_groups',
                                         through='authentication.GroupPermission')
 
    def __unicode__(self):
        return self.group_name
    
    class Meta:
        verbose_name = "group"
        verbose_name_plural = "groups"
    
    
    
class Membership(models.Model):
    """The Membership model combines the User and Group model.
    It contains the information which user is in which group."""
    
    user = models.ForeignKey('authentication.User')
    group = models.ForeignKey('authentication.Group')
    
    def __unicode__(self):
        return 'User: %s | Group: %s' % (self.user, self.group) 



class GroupPermission(models.Model):
    """This model manages the permissions of each group
    relating to their collections."""
    
    collection = models.ForeignKey('collection.Collection')
    group = models.ForeignKey('authentication.Group')
    
    permission = models.CharField(verbose_name=u'permission',
                                  max_length=1,
                                  choices=Permission.CHOICES,
                                  default=Permission.READ)
    
    def __unicode__(self):
        return 'Group: %s | Collection ID: %d | Permission: %s' % (self.group, 
                                                                   self.collection.directory.identifier,
                                                                   self.permission)
    


class UserPermission(models.Model):
    """This model manages the permissions of each user
    relating to their collections."""
    
    collection = models.ForeignKey('collection.Collection')
    user = models.ForeignKey('authentication.User')
    
    permission = models.CharField(verbose_name=u'permission',
                                  max_length=1,
                                  choices=Permission.CHOICES,
                                  default=Permission.READ)
    
    def __unicode__(self):
        return 'User: %s | Collection ID: %d | Permission: %s' % (self.user, 
                                                                  self.collection.directory.identifier,
                                                                  self.permission)

#

class Subscription(models.Model):
    """This model manages all subscribed collections of
    each user."""
    
    collection = models.ForeignKey('collection.Collection')
    user = models.ForeignKey('authentication.User')
    
    date_subscribed = models.DateField(verbose_name=u'date subscribed',
                                       auto_now_add=True, 
                                       editable=False)
    
    def __unicode__(self):
        return 'User: %s | Collection ID: %d' % (self.user, 
                                                 self.collection.directory.identifier)
    
    
    