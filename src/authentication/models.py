from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import IntegrityError
from utils import enum
from chiara.settings.common import WEBDAV_DIR
import os, shutil

import logging
logger = logging.getLogger(__name__)

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
    
    def get_permission(self, collection):
        access = None
        if self.userpermission_set.filter(collection=collection):
            access = self.userpermission_set.get(collection=collection).permission
        if access != enum.Permission.WRITE:
            for group in self.groups.all():
                if group.grouppermission_set.filter(collection=collection):
                    if group.grouppermission_set.get(collection=collection).permission == enum.Permission.WRITE:
                        return enum.Permission.WRITE
        
        return access
    
    def get_all_permissible_collections(self):
        """Return all permissible collections (inclusive all permissions of belonging groups)."""
        return list(set([c for g in self.groups.all() for c in g.permissions.all()] + list(self.permissions.all())))

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_admin

    def __unicode__(self):
        return self.user_name
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(AbstractBaseUser, self).save(force_insert=force_insert, force_update=force_update, 
                                       using=using, update_fields=update_fields)
        # create WebDAV directory
        webdav_path = os.path.join(WEBDAV_DIR, self.user_name)
        if not os.path.exists(webdav_path):
            os.makedirs(webdav_path)
    
    def delete(self, using=None):
        super(AbstractBaseUser, self).delete(using=using)       
        # remove WebDAV directory
        webdav_path = os.path.join(WEBDAV_DIR, self.user_name)
        if os.path.exists(webdav_path):
            shutil.rmtree(webdav_path)
    
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
                                  choices=enum.Permission.CHOICES,
                                  default=enum.Permission.READ)
    
    @staticmethod
    def update(collection):
        """Update the permission to the given collection of all users who has permission
        to the previous one."""
        prev_col = collection.get_revision(collection.revision-1)
        for prev_up in prev_col.grouppermission_set.all():
            try:
                gp = GroupPermission(collection=collection,
                                     group=prev_up.group,
                                     permission=prev_up.permission)
                gp.save()
            except IntegrityError:
                pass
    
    def save_all_revisions(self):
        """Set permission to all revisions of the collection."""
        for c in self.collection.get_all_revisions():
            try:
                if GroupPermission.objects.filter(group=self.group, collection=c):
                    gp = GroupPermission.objects.get(group=self.group, collection=c)
                    gp.permission = self.permission
                else:
                    gp = GroupPermission(collection=c,
                                         group=self.group,
                                         permission=self.permission)
                gp.save()
            except IntegrityError:
                pass 
    
    def delete_all_revisions(self):
        """Delete permissions of all revisions of the collection."""
        # Delete permission
        for c in self.collection.get_all_revisions():
            try:
                if GroupPermission.objects.filter(group=self.group, collection=c):
                    gp = GroupPermission.objects.get(group=self.group, collection=c)
                    gp.delete()
            except IntegrityError:
                pass

        self.delete()
        # Delete subscription
        for c in self.collection.get_all_revisions():
            try:
                for u in c.users_who_subscribed.all():
                    if c not in u.get_all_permissible_collections() and Subscription.objects.filter(user=u, collection=c):
                        subscription = Subscription.objects.get(user=u, collection=c)
                        subscription.delete()
            except IntegrityError:
                pass
        

    def __unicode__(self):
        return 'Group: %s | Collection ID: %d | Permission: %s' % (self.group, 
                                                                   self.collection.directory.identifier,
                                                                   self.permission)
        
    class Meta:
        unique_together = (("collection", "group"),)
    


class UserPermission(models.Model):
    """This model manages the permissions of each user
    relating to their collections."""
    
    collection = models.ForeignKey('collection.Collection')
    user = models.ForeignKey('authentication.User')
    
    permission = models.CharField(verbose_name=u'permission',
                                  max_length=1,
                                  choices=enum.Permission.CHOICES,
                                  default=enum.Permission.READ)
    
    @staticmethod
    def update(collection):
        """Update the permission to the given collection of all users who has permission
        to the previous one."""
        prev_col = collection.get_revision(collection.revision-1)
        for prev_up in prev_col.userpermission_set.all():
            try:
                up = UserPermission(collection=collection,
                                    user=prev_up.user,
                                    permission=prev_up.permission)
                up.save()
            except IntegrityError:
                pass
    
    def save_all_revisions(self):
        """Set permission to all revisions of the collection."""
        for c in self.collection.get_all_revisions():
            try:
                if UserPermission.objects.filter(user=self.user, collection=c):
                    up = UserPermission.objects.get(user=self.user, collection=c)
                    up.permission = self.permission
                else:
                    up = UserPermission(collection=c,
                                    user=self.user,
                                    permission=self.permission)
                up.save()
            except IntegrityError:
                pass  
    
    def delete_all_revisions(self):
        """Delete permissions of all revisions of the collection."""
        # Delete permission
        for c in self.collection.get_all_revisions():
            try:
                if UserPermission.objects.filter(user=self.user, collection=c):
                    up = UserPermission.objects.get(user=self.user, collection=c)
                    up.delete()
            except IntegrityError:
                pass
        self.delete()
        # Delete subscription
        for c in self.collection.get_all_revisions():
            try:
                if Subscription.objects.filter(user=self.user, collection=c):
                    subscription = Subscription.objects.get(user=self.user, collection=c)
                    subscription.delete()
            except IntegrityError:
                pass

    
    def __unicode__(self):
        return 'User: %s | Collection ID: %d | Permission: %s' % (self.user, 
                                                                  self.collection.directory.identifier,
                                                                  self.permission)
    class Meta:
        unique_together = (("collection", "user"),)


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
    
    def save(self, *args, **kwargs):
        # remove all subscribed revisions of this collection
        cols_with_same_id = self.user.subscriptions.filter(identifier=self.collection.identifier)
        for c in cols_with_same_id:
            subscription = Subscription.objects.get(user=self.user, collection=c)
            subscription.delete()
        
        super(Subscription, self).save()
        
    class Meta:
        unique_together = (("collection", "user"),)
    
