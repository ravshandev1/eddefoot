from rest_framework import views, generics, response, status, permissions
from rest_framework.authtoken.models import Token
from random import randint
from datetime import date, datetime, timedelta
from pytz import timezone
from django.conf import settings
from django.db.models import Q
from . import models
from . import serializers
from .permissions import IsStudentUser, IsParentUser, IsCoachUser, IsPsychologicalUser
from .paginations import CustomPagination
from .utils import verify, subscribe
from .tasks import send_notification_task
from .payment import client, client_receipt
from exercise.models import Rate, PriceOfSubscribe


class StudentChatAPI(views.APIView):
    permission_classes = [IsStudentUser]

    def get(self, request, *args, **kwargs):
        ls = list()
        coach = models.Coach.objects.filter(sub_class__student=self.request.user).first()
        dt = serializers.StudentChatSerializer(coach).data
        mes = models.Message.objects.filter(sender_id=coach.user.id, receiver_id=self.request.user.id, seen=False)
        dt['messages_count'] = mes.count()
        ls.append(dt)
        ps = models.Psychological.objects.filter(sub_class__student=self.request.user).first()
        dt = serializers.StudentChatSerializer(ps).data
        mes = models.Message.objects.filter(sender_id=ps.user.id, receiver_id=self.request.user.id, seen=False)
        dt['messages_count'] = mes.count()
        ls.append(dt)
        for i in self.request.user.parent.all():
            dt = serializers.StudentChatSerializer(i).data
            mes = models.Message.objects.filter(sender_id=i.user.id, receiver_id=self.request.user.id, seen=False)
            dt['messages_count'] = mes.count()
            ls.append(dt)
        return response.Response(ls)


class ParentChatAPI(views.APIView):
    permission_classes = [IsParentUser]

    def get(self, request, *args, **kwargs):
        data = list()
        for i in self.request.user.children.children.all():
            dt = serializers.ParentChatSerializer(i).data
            mes = models.Message.objects.filter(sender_id=i.id, receiver_id=self.request.user.id, seen=False)
            dt['messages_count'] = mes.count()
            data.append(dt)
            coach = models.Coach.objects.filter(sub_class__student=i).first()
            dt = serializers.StudentChatSerializer(coach).data
            mes = models.Message.objects.filter(sender_id=coach.user.id, receiver_id=self.request.user.id, seen=False)
            dt['messages_count'] = mes.count()
            dt['student'] = i.name
            data.append(dt)
            ps = models.Psychological.objects.filter(sub_class__student=i).first()
            dt = serializers.StudentChatSerializer(ps).data
            mes = models.Message.objects.filter(sender_id=ps.user.id, receiver_id=self.request.user.id, seen=False)
            dt['messages_count'] = mes.count()
            dt['student'] = i.name
            data.append(dt)
        return response.Response(data)


class CoachChatAPI(views.APIView):
    permission_classes = [IsCoachUser]

    def get(self, request, *args, **kwargs):
        data = list()
        for i in self.request.user.my_students.sub_class.all():
            dt = serializers.CoachChatSerializer(i).data
            mes = models.Message.objects.filter(sender_id=i.id, receiver_id=self.request.user.id, seen=False)
            dt['messages_count'] = mes.count()
            data.append(dt)
            for j in models.Parent.objects.filter(children=i.student):
                dt = serializers.StudentChatSerializer(j).data
                mes = models.Message.objects.filter(sender_id=j.user.id, receiver_id=self.request.user.id, seen=False)
                dt['messages_count'] = mes.count()
                dt['child'] = i.student.name
                data.append(dt)
        return response.Response(data)


class PsychologistChatAPI(views.APIView):
    permission_classes = [IsPsychologicalUser]

    def get(self, request, *args, **kwargs):

        data = list()
        for i in self.request.user.students.sub_class.all():
            dt = serializers.CoachChatSerializer(i).data
            mes = models.Message.objects.filter(sender_id=i.id, receiver_id=self.request.user.id, seen=False)
            dt['messages_count'] = mes.count()
            data.append(dt)
            for j in models.Parent.objects.filter(children=i.student):
                dt = serializers.StudentChatSerializer(j).data
                mes = models.Message.objects.filter(sender_id=j.user.id, receiver_id=self.request.user.id, seen=False)
                dt['messages_count'] = mes.count()
                dt['child'] = i.student.name
                data.append(dt)
        return response.Response(data)


class ChatRoomAPI(generics.ListAPIView):
    pagination_class = CustomPagination
    serializer_class = serializers.ChatSerializer
    queryset = models.Message.objects.all()

    def get(self, request, *args, **kwargs):
        s_id = self.request.query_params.get('sender_id')
        r_id = self.request.query_params.get('receiver_id')
        if s_id and r_id:
            chat_room = models.ChatRoom.objects.filter(
                Q(sender_id=s_id, receiver_id=r_id) | Q(sender_id=r_id, receiver_id=s_id)).first()
            if chat_room is None:
                chat_room = models.ChatRoom.objects.create(sender_id=s_id, receiver_id=r_id)
            qs = self.filter_queryset(models.Message.objects.filter(room_id=chat_room))
            page = self.paginate_queryset(qs)
            messages = list()
            for i in page:
                if i.sender.id == int(s_id):
                    messages.append({'id': i.id, 'owner': 'sender', 'message': i.message, 'seen': i.seen,
                                     'created_at': i.created_at.__format__("%-d/%m/%Y, %H:%M")})
                else:
                    messages.append({'id': i.id, 'owner': 'receiver', 'message': i.message,
                                     'created_at': i.created_at.__format__("%-d/%m/%Y, %H:%M")})
            return self.get_paginated_response({'id': chat_room.id, 'messages': messages})
        return response.Response({'success': False, 'message': 'You forgot to give receiver_id or sender_id'})


class CardCreateAPI(views.APIView):
    def post(self, request, *args, **kwargs):
        card_number = self.request.data.get('card_number')
        expire_date = self.request.data.get('expire_date')
        res = client.cards_create(number=card_number, expire=expire_date, save=False)
        try:
            token = res['result']['card']['token']
        except Exception as e:
            print(e)
            return response.Response({'success': False, 'results': res['error']['message']},
                                     status=status.HTTP_400_BAD_REQUEST)
        client.card_get_verify_code(token)
        return response.Response({'success': True, 'results': {'token': token}})


class CardVerifyAPI(views.APIView):
    def post(self, request, *args, **kwargs):
        verify_code = self.request.data.get('code')
        token = self.request.data.get('token')
        res = client.cards_verify(verify_code, token)
        try:
            token = res['result']['card']['token']
        except Exception as e:
            print(e)
            return response.Response({'success': False, 'results': res['error']['message']},
                                     status=status.HTTP_400_BAD_REQUEST)
        check = client.cards_check(token)
        if check['result']['card']['verify']:
            return response.Response({'success': True, 'results': "Card verified successfully"})
        else:
            return response.Response({'success': False, 'results': check['error']['message']},
                                     status=status.HTTP_400_BAD_REQUEST)


class StudentRatePayAPI(views.APIView):
    permission_classes = [IsStudentUser]

    def post(self, request, *args, **kwargs):
        pk = self.request.data.get('rate_id')
        rate = Rate.objects.filter(id=pk).first()
        if rate.price > 0:
            token = self.request.data.get('token')
            res = client_receipt.receipts_create(rate.id, float(rate.price * 100), self.request.user.id,
                                                 rate.description)
            try:
                invoice_id = res['result']['receipt']['_id']
            except Exception as e:
                print(e)
                return response.Response({'success': False, 'results': res['error']['message']},
                                         status=status.HTTP_400_BAD_REQUEST)
            pay = client_receipt.receipts_pay(rate.id, invoice_id, token, self.request.user.phone)
            try:
                pay['result']['receipt']['_id']
            except Exception as e:
                print(e)
                return response.Response({'success': False, 'results': pay['error']['message']},
                                         status=status.HTTP_400_BAD_REQUEST)
            self.request.user.rate = rate
            self.request.user.save()
            obj = models.Payment.objects.filter(user=self.request.user).first()
            if obj:
                if obj.ended_at >= datetime.now(timezone(settings.TIME_ZONE)):
                    obj.ended_at += timedelta(days=365)
                else:
                    obj.ended_at = datetime.now(timezone(settings.TIME_ZONE)) + timedelta(days=365)
                obj.save()
            else:
                models.Payment.objects.create(user=self.request.user,
                                              ended_at=datetime.now(timezone(settings.TIME_ZONE)) + timedelta(
                                                  days=365))
            return response.Response({'success': True, 'results': 'Your payment was made successfully'})
        else:
            self.request.user.rate = rate
            self.request.user.save()
            obj = models.Payment.objects.filter(user=self.request.user).first()
            if obj:
                if obj.ended_at >= datetime.now(timezone(settings.TIME_ZONE)):
                    obj.ended_at += timedelta(days=365)
                else:
                    obj.ended_at = datetime.now(timezone(settings.TIME_ZONE)) + timedelta(days=365)
                obj.save()
            else:
                models.Payment.objects.create(user=self.request.user,
                                              ended_at=datetime.now(timezone(settings.TIME_ZONE)) + timedelta(
                                                  days=365))
            return response.Response({'success': True, 'results': 'Your payment was made successfully'})


class ParentRatePayAPI(views.APIView):
    permission_classes = [IsParentUser]

    def post(self, request, *args, **kwargs):
        pk = self.request.data.get('rate_id')
        child_id = self.request.data.get('child_id')
        user = models.User.objects.filter(id=child_id).first()
        rate = Rate.objects.filter(id=pk).first()
        if rate.price > 0:
            token = self.request.data.get('token')
            res = client_receipt.receipts_create(rate.id, float(rate.price * 100), user.id, rate.description)
            try:
                invoice_id = res['result']['receipt']['_id']
            except Exception as e:
                print(e)
                return response.Response({'success': False, 'results': res['error']['message']},
                                         status=status.HTTP_400_BAD_REQUEST)
            pay = client_receipt.receipts_pay(rate.id, invoice_id, token, user.phone)
            try:
                pay['result']['receipt']['_id']
            except Exception as e:
                print(e)
                return response.Response({'success': False, 'results': pay['error']['message']},
                                         status=status.HTTP_400_BAD_REQUEST)
            user.rate = rate
            user.save()
            obj = models.Payment.objects.filter(user=user).first()
            if obj:
                if obj.ended_at >= datetime.now(timezone(settings.TIME_ZONE)):
                    obj.ended_at += timedelta(days=365)
                else:
                    obj.ended_at = datetime.now(timezone(settings.TIME_ZONE)) + timedelta(days=365)
                obj.save()
            else:
                models.Payment.objects.create(user=user,
                                              ended_at=datetime.now(timezone(settings.TIME_ZONE)) + timedelta(
                                                  days=365))
            return response.Response({'success': True, 'results': 'Your payment was made successfully'})
        else:
            user.rate = rate
            user.save()
            obj = models.Payment.objects.filter(user=user).first()
            if obj:
                if obj.ended_at >= datetime.now(timezone(settings.TIME_ZONE)):
                    obj.ended_at += timedelta(days=365)
                else:
                    obj.ended_at = datetime.now(timezone(settings.TIME_ZONE)) + timedelta(days=365)
                obj.save()
            else:
                models.Payment.objects.create(user=user,
                                              ended_at=datetime.now(timezone(settings.TIME_ZONE)) + timedelta(
                                                  days=365))
            return response.Response({'success': True, 'results': 'Your payment was made successfully'})


class SubscribeStudentAPI(views.APIView):
    permission_classes = [IsStudentUser]

    def post(self, request, *args, **kwargs):
        token = self.request.data.get('token')
        price = PriceOfSubscribe.objects.first()
        res = client_receipt.receipts_create(price.id, float(price.price * 100), self.request.user.id,
                                             'Subscribe for a year')
        try:
            invoice_id = res['result']['receipt']['_id']
        except Exception as e:
            print(e)
            return response.Response({'success': False, 'results': res['error']['message']},
                                     status=status.HTTP_400_BAD_REQUEST)
        pay = client_receipt.receipts_pay(price.id, invoice_id, token, self.request.user.phone)
        try:
            pay['result']['receipt']['_id']
        except Exception as e:
            print(e)
            return response.Response({'success': False, 'results': pay['error']['message']},
                                     status=status.HTTP_400_BAD_REQUEST)
        obj = models.Payment.objects.filter(user=self.request.user).first()
        if obj:
            if obj.ended_at >= datetime.now(timezone(settings.TIME_ZONE)):
                obj.ended_at += timedelta(days=365)
            else:
                obj.ended_at = datetime.now(timezone(settings.TIME_ZONE)) + timedelta(days=365)
            obj.save()
        else:
            models.Payment.objects.create(user=self.request.user,
                                          ended_at=datetime.now(timezone(settings.TIME_ZONE)) + timedelta(
                                              days=365))
        return response.Response({'success': True})


class SubscribeParentAPI(views.APIView):
    permission_classes = [IsParentUser]

    def post(self, request, *args, **kwargs):
        token = self.request.data.get('token')
        user = models.User.objects.filter(id=self.request.data.get('child_id')).first()
        price = PriceOfSubscribe.objects.first()
        res = client_receipt.receipts_create(price.id, float(price.price * 100), user.id,
                                             'Subscribe for a year')
        try:
            invoice_id = res['result']['receipt']['_id']
        except Exception as e:
            print(e)
            return response.Response({'success': False, 'results': res['error']['message']},
                                     status=status.HTTP_400_BAD_REQUEST)
        pay = client_receipt.receipts_pay(price.id, invoice_id, token, user.phone)
        try:
            pay['result']['receipt']['_id']
        except Exception as e:
            print(e)
            return response.Response({'success': False, 'results': pay['error']['message']},
                                     status=status.HTTP_400_BAD_REQUEST)
        obj = models.Payment.objects.filter(user=user).first()
        if obj:
            if obj.ended_at >= datetime.now(timezone(settings.TIME_ZONE)):
                obj.ended_at += timedelta(days=365)
            else:
                obj.ended_at = datetime.now(timezone(settings.TIME_ZONE)) + timedelta(days=365)
            obj.save()
        else:
            models.Payment.objects.create(user=user, ended_at=datetime.now(timezone(settings.TIME_ZONE)) + timedelta(
                days=365))
        return response.Response({'success': True})


class FeedbackAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = dict()
        data['text'] = self.request.data.get('text', None)
        data['user'] = self.request.user.id
        data['video'] = self.request.data.get('video', None)
        data['image'] = self.request.data.get('image', None)
        serializer = serializers.FeedbackSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)


class CoachStudentsRatingAPI(generics.ListAPIView):
    permission_classes = [IsCoachUser]
    pagination_class = CustomPagination
    serializer_class = serializers.StudentRatingSerializer

    def get_queryset(self):
        ls = list()
        for i in self.request.user.my_students.sub_class.all():
            ls.append(i)
        ls.sort(key=lambda x: x.student.point, reverse=True)
        return ls


class PsychologicalStudentsRatingAPI(generics.ListAPIView):
    permission_classes = [IsPsychologicalUser]
    pagination_class = CustomPagination
    serializer_class = serializers.StudentRatingSerializer

    def get_queryset(self):
        ls = list()
        for i in self.request.user.students.sub_class.all():
            ls.append(i)
        ls.sort(key=lambda x: x.student.point, reverse=True)
        return ls


class MyChildPlanAPI(generics.ListAPIView):
    permission_classes = [IsParentUser]
    pagination_class = CustomPagination
    serializer_class = serializers.StudentPlanSerializer

    def get_queryset(self):
        return models.MyPlan.objects.filter(user_id=self.kwargs.get('pk'))


class StudentPlanAPI(generics.ListAPIView):
    pagination_class = CustomPagination
    serializer_class = serializers.StudentPlanSerializer

    def get_queryset(self):
        return models.MyPlan.objects.filter(user_id=self.kwargs.get('pk'))


class AgeAPI(generics.ListAPIView):
    queryset = models.Age.objects.all()
    serializer_class = serializers.AgeSerializer
    pagination_class = CustomPagination


class LevelAPI(generics.ListAPIView):
    queryset = models.Level.objects.all()
    serializer_class = serializers.LevelSerializer
    pagination_class = CustomPagination


class RatingAPI(generics.ListAPIView):
    pagination_class = CustomPagination
    serializer_class = serializers.RatingSerializer

    def get_queryset(self):
        return models.User.objects.filter(role=0).order_by('-point')


class StudentLoginAPI(views.APIView):

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get('phone', None)
        # code = str(randint(10000, 100000))
        code = '77777'
        verify(phone, code)
        models.VerifyPhone.objects.create(phone=phone, code=code)
        user = models.User.objects.filter(phone=phone).first()
        if user is None:
            user = models.User.objects.create_user(phone=phone, password='1')
            Token.objects.create(user_id=user.id)
            user.role = 0
            user.save()
            return response.Response(
                {'success': True, 'message': 'User registered verification code was sent to your phone',
                 'is_registered': True}, status=status.HTTP_201_CREATED)
        elif user:
            return response.Response({'success': True, 'message': 'Verification code was sent to your phone',
                                      'is_registered': False})


class ParentLoginAPI(views.APIView):

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get('phone', None)
        # code = str(randint(10000, 100000))
        code = '77777'
        verify(phone, code)
        models.VerifyPhone.objects.create(phone=phone, code=code)
        user = models.User.objects.filter(phone=phone).first()
        if user is None:
            user = models.User.objects.create_user(phone=phone, password='1')
            user.role = 1
            user.save()
            Token.objects.create(user_id=user.id)
            models.Parent.objects.create(user_id=user.id)
            return response.Response(
                {'success': True, 'message': 'User registered verification code was sent to your phone',
                 'is_registered': True}, status=status.HTTP_201_CREATED)
        elif user:
            return response.Response({'success': True, 'message': 'Verification code was sent to your phone',
                                      'is_registered': False})


class CoachLoginAPI(views.APIView):

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get('phone', None)
        # code = str(randint(10000, 100000))
        code = '77777'
        verify(phone, code)
        models.VerifyPhone.objects.create(phone=phone, code=code)
        user = models.User.objects.filter(phone=phone).first()
        if user is None:
            user = models.User.objects.create_user(phone=phone, password='1')
            user.role = 2
            user.save()
            Token.objects.create(user_id=user.id)
            models.Coach.objects.create(user_id=user.id)
            return response.Response(
                {'success': True, 'message': 'User registered verification code was sent to your phone',
                 'is_registered': True}, status=status.HTTP_201_CREATED)
        elif user:
            return response.Response({'success': True, 'message': 'Verification code was sent to your phone',
                                      'is_registered': False})


class PLoginAPI(views.APIView):

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get('phone', None)
        # code = str(randint(10000, 100000))
        code = '77777'
        verify(phone, code)
        models.VerifyPhone.objects.create(phone=phone, code=code)
        user = models.User.objects.filter(phone=phone).first()
        if user is None:
            user = models.User.objects.create_user(phone=phone, password='1')
            user.role = 3
            user.save()
            Token.objects.create(user_id=user.id)
            models.Psychological.objects.create(user_id=user.id)
            return response.Response(
                {'success': True, 'message': 'User registered verification code was sent to your phone',
                 'is_registered': True}, status=status.HTTP_201_CREATED)
        elif user:
            return response.Response({'success': True, 'message': 'Verification code was sent to your phone',
                                      'is_registered': False})


class VerifyPhoneAPI(views.APIView):

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get('phone', None)
        code = self.request.data.get('code', None)
        v = models.VerifyPhone.objects.filter(phone=phone, code=code).first()
        if v:
            user = models.User.objects.filter(phone=phone).first()
            v.delete()
            if user.role == 0:
                data = serializers.StudentSerializer(instance=user).data
            else:
                data = serializers.UserSerializer(instance=user).data
            token = Token.objects.get(user=user)
            data['token'] = token.key
            return response.Response(data)
        else:
            return response.Response({'success': False, 'message': "Verification code incorrect!"},
                                     status=status.HTTP_400_BAD_REQUEST)


class RequestJoinAPI(views.APIView):

    def post(self, request):
        phone = self.request.data.get('phone', None)
        # code = str(randint(10000, 100000))
        code = '77777'
        verify(phone, code)
        models.VerifyPhone.objects.create(phone=phone, code=code)
        return response.Response(
            {'success': True, 'message': 'Verification code was sent to your child phone'})


class JoinAPI(views.APIView):
    permission_classes = [IsParentUser]

    def post(self, request, *args, **kwargs):
        phone = self.request.data.get('phone', None)
        code = self.request.data.get('code', None)
        v = models.VerifyPhone.objects.filter(phone=phone, code=code).first()
        if v:
            child = models.User.objects.filter(phone=phone).first()
            obj = models.Parent.objects.filter(user_id=self.request.user.id).first()
            obj.children.add(child)
            v.delete()
            return response.Response({'success': True, 'message': "Your child joined"})
        return response.Response({'success': False, 'message': "Verification code incorrect!"})


class QrJoinAPI(views.APIView):
    permission_classes = [IsParentUser]

    def post(self, request, *args, **kwargs):
        child = models.User.objects.filter(id=self.request.data['id']).first()
        obj = models.Parent.objects.filter(user_id=self.request.user.id).first()
        obj.children.add(child)
        return response.Response({'success': True, 'message': "Your child joined"})


class MyChildrenAPI(generics.ListAPIView):
    permission_classes = [IsParentUser]
    pagination_class = CustomPagination
    serializer_class = serializers.ChildSerializer

    def get_queryset(self):
        obj = models.Parent.objects.filter(user_id=self.request.user.id).first()
        return obj.children.all()


class UserAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if self.request.user.role == 0:
            serializer = serializers.StudentSerializer(instance=self.request.user, data=self.request.data, partial=True)
        else:
            serializer = serializers.UserSerializer(instance=self.request.user, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)

    def get(self, request, *args, **kwargs):
        if self.request.user.role == 0:
            serializer = serializers.StudentSerializer(instance=self.request.user)
        else:
            serializer = serializers.UserSerializer(instance=self.request.user)
        return response.Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        self.request.user.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class MyPlanModulsAPI(generics.ListAPIView):
    permission_classes = [IsStudentUser]
    pagination_class = CustomPagination
    serializer_class = serializers.MyPlanModulSerializer

    def get_queryset(self):
        return models.MyPlan.objects.filter(user_id=self.request.user.id).order_by('exercise__theme__modul').distinct(
            'exercise__theme__modul')

    def get(self, request, *args, **kwargs):
        if subscribe(self.request.user):
            return response.Response({'success': False, 'results': 'Your subscribe expired. Please subscribe now!'},
                                     status=status.HTTP_402_PAYMENT_REQUIRED)
        return self.list(request, *args, **kwargs)


class MyPlanThemesAPI(generics.ListAPIView):
    pagination_class = CustomPagination
    serializer_class = serializers.MyPlanThemeSerializer

    def get_queryset(self):
        return models.MyPlan.objects.filter(exercise__theme__modul_id=self.kwargs.get('pk')).order_by(
            'exercise__theme').distinct('exercise__theme')


class MyPlanExercisesAPI(generics.ListAPIView):
    permission_classes = [IsStudentUser]
    serializer_class = serializers.MyPlanExerciseSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        theme_id = self.request.query_params.get('theme_id')
        is_view = self.request.query_params.get('is_view')
        if theme_id:
            return models.MyPlan.objects.filter(exercise__theme_id=theme_id, user_id=self.request.user).order_by(
                'exercise__ordinal_number')
        if is_view:
            obj = models.MyPlan.objects.filter(exercise_id=is_view, user_id=self.request.user.id).first()
            obj.date = date.today()
            percent = 50 / obj.exercise.do_day
            obj.percent += percent
            obj.save()
        return models.MyPlan.objects.filter(user_id=self.request.user.id).order_by('exercise__ordinal_number')

    def post(self, request, *args, **kwargs):
        for i in self.request.data['exercises']:
            models.MyPlan.objects.create(user_id=self.request.user.id, exercise_id=i)
        return response.Response({'success': True}, status=status.HTTP_201_CREATED)


class ExerciseAnswerAPI(views.APIView):
    permission_classes = [IsStudentUser]

    def post(self, request, *args, **kwargs):
        data = dict()
        data['user'] = self.request.user.id
        data['exercise'] = self.request.data['exercise']
        data['video'] = self.request.data['video']
        data['description'] = self.request.data['description']
        serializer = serializers.ExerciseAnswerSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        obj = models.MyPlan.objects.filter(user_id=self.request.user.id, exercise_id=data['exercise']).first()
        obj.date = date.today()
        percent = 50 / obj.exercise.do_day
        obj.percent += percent
        obj.save()
        return response.Response(serializer.data)


class PointExerciseAPI(views.APIView):
    permission_classes = [IsCoachUser]

    def patch(self, request, *args, **kwargs):
        obj = models.ExerciseAnswer.objects.filter(id=self.kwargs.get('pk')).first()
        obj.point = self.request.data['point']
        obj.save()
        user = obj.user
        exercise = obj.exercise
        user.point += self.request.data['point']
        user.save()
        my_plan = models.MyPlan.objects.filter(user=user, exercise=exercise).first()
        if my_plan.percent == 100.00:
            my_plan.delete()
        models.DoneExercise.objects.create(user=user, exercise=exercise)
        text_en = f"Coach {obj.point} marked your exercise"
        text_uz = f"Murabbiy sizning mashqingizga {obj.point} ball qo'ydi"
        text_ru = f"Тренер {obj.point} отметил ваше упражнение"
        send_notification_task.delay(students=[obj.user.id], text_en=text_en, text_ru=text_ru, text_uz=text_uz)
        return response.Response({'success': True})


class DoneExerciseAPI(generics.ListAPIView):
    permission_classes = [IsStudentUser]
    pagination_class = CustomPagination
    serializer_class = serializers.DoneExerciseSerializer

    def get_queryset(self):
        return models.DoneExercise.objects.filter(user_id=self.request.user.id)


class LessonCoachAPI(generics.ListAPIView):
    permission_classes = [IsCoachUser]
    serializer_class = serializers.LessonsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.request.user.my_lessons.all()

    def post(self, request, *args, **kwargs):
        data = dict()
        data['sender'] = self.request.user.id
        data['students'] = [i.student.id for i in self.request.user.my_students.sub_class.all()]
        data['name'] = self.request.data['name']
        data['image'] = self.request.data['image']
        data['link'] = self.request.data['link']
        data['password'] = self.request.data['password']
        data['date'] = self.request.data['date']
        serializer = serializers.LessonSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        text_en = f"Coach marked your exercise"
        text_uz = f"Murabbiy sizning mashqingizni belgilab qo'ydi"
        text_ru = f"Тренер отметил ваше упражнение"
        send_notification_task.delay(students=data['students'], text_en=text_en, text_ru=text_ru, text_uz=text_uz)
        return response.Response({'success': True}, status=status.HTTP_201_CREATED)


class LessonPsychologicalAPI(generics.ListAPIView):
    permission_classes = [IsPsychologicalUser]
    pagination_class = CustomPagination
    serializer_class = serializers.LessonsSerializer

    def get_queryset(self):
        return self.request.user.my_lessons.all()

    def post(self, request, *args, **kwargs):
        data = dict()
        data['sender'] = self.request.user.id
        data['students'] = [i.student.id for i in self.request.user.students.sub_class.all()]
        data['name'] = self.request.data['name']
        data['image'] = self.request.data['image']
        data['link'] = self.request.data['link']
        data['password'] = self.request.data['password']
        data['date'] = self.request.data['date']
        serializer = serializers.LessonSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        text_en = f"Psychologist marked your exercise"
        text_uz = f"Psixolig sizning mashqingizni belgilab qo'ydi"
        text_ru = f"Психолог отметил ваше упражнение"
        send_notification_task.delay(students=data['students'], text_en=text_en, text_ru=text_ru, text_uz=text_uz)
        return response.Response({'success': True}, status=status.HTTP_201_CREATED)


class NotificationAPI(generics.ListAPIView):
    pagination_class = CustomPagination
    serializer_class = serializers.NotificationSerializer
    permission_classes = [IsStudentUser]

    def get_queryset(self):
        return models.Notification.objects.filter(user_id=self.request.user.id)

    def patch(self, request, *args, **kwargs):
        obj = models.Notification.objects.filter(id=self.request.data.get('id')).first()
        obj.is_read = True
        obj.save()
        return response.Response({'success': True})


class LessonStudentAPI(generics.ListAPIView):
    serializer_class = serializers.LessonStudentSerializer
    permission_classes = [IsStudentUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return models.Lesson.objects.filter(students=self.request.user)
