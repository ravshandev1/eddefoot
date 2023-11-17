from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from exercise.models import Rate, Exercise


class Level(models.Model):
    name = models.CharField(max_length=250)
    icon = models.ImageField(upload_to='levels')
    subtext = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Age(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **kwargs):
        if not phone:
            raise TypeError('Phone did not come')
        user = self.model(phone=phone, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **kwargs):
        if not password:
            raise TypeError('Password did not come')
        user = self.create_user(phone, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    GANDER = (
        (0, "MALE"),
        (1, "FEMALE")
    )
    ROLE = (
        (0, 'Student'),
        (1, 'Parent'),
        (2, 'Coach'),
        (3, 'Psychologist')
    )
    phone = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='users', null=True)
    level = models.ForeignKey(Level, models.SET_NULL, null=True)
    age = models.ForeignKey(Age, models.SET_NULL, null=True)
    point = models.PositiveIntegerField(default=0)
    gender = models.PositiveIntegerField(choices=GANDER, default=0)
    role = models.PositiveIntegerField(default=0, choices=ROLE)
    rate = models.ForeignKey(Rate, models.SET_NULL, null=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'phone'

    def __str__(self):
        return self.phone


class Parent(models.Model):
    user = models.OneToOneField(User, models.CASCADE, related_name='children', limit_choices_to={'role': 1})
    children = models.ManyToManyField(User, related_name='parent', limit_choices_to={'role': 0})

    def __str__(self):
        return self.user.phone


class Coach(models.Model):
    user = models.OneToOneField(User, models.CASCADE, related_name='my_students', limit_choices_to={'role': 2})
    students = models.ManyToManyField(User, related_name='coach', limit_choices_to={'role': 0})

    def __str__(self):
        return self.user.phone


class Psychological(models.Model):
    user = models.OneToOneField(User, models.CASCADE, related_name='students', limit_choices_to={'role': 3})
    students = models.ManyToManyField(User, related_name='psychological', limit_choices_to={'role': 0})

    def __str__(self):
        return self.user.phone


class Chat(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(User, models.CASCADE, related_name='senders')
    receiver = models.ForeignKey(User, models.CASCADE, related_name='receivers')
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class Payment(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='payments')
    ended_at = models.DateTimeField()

    def __str__(self):
        return self.user.phone


class VerifyPhone(models.Model):
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.phone


class Lesson(models.Model):
    sender = models.ForeignKey(User, models.SET_NULL, null=True, related_name='my_lessons')
    students = models.ManyToManyField(User, related_name='lessons')
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='lessons')
    link = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    date = models.DateTimeField()

    def __str__(self):
        return self.name


class ParentControl(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='parent_controls')
    time = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.phone


class Feedback(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    image = models.ImageField(upload_to='feedback', null=True, blank=True)
    video = models.FileField(upload_to='feedback', null=True, blank=True)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.phone


class MyPlan(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='my_plan')
    exercise = models.ForeignKey(Exercise, models.CASCADE, related_name='my_plan')
    percent = models.FloatField(default=0)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.phone


class DoneExercise(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='done_exercises')
    exercise = models.ForeignKey(Exercise, models.CASCADE, related_name='done_exercises')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.phone


class ExerciseAnswer(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='exercise_answers')
    exercise = models.ForeignKey(Exercise, models.CASCADE, related_name='exercise_answers')
    video = models.FileField(upload_to='exercise_answers')
    point = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.phone


class Notification(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='notifications')
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.phone
