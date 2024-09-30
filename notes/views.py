from django.shortcuts import render
from notes.models import User,Task
from django.db.models import Count

# Create your views here.
from notes.serializers import UserSerializer,Taskserializer
from rest_framework import generics,permissions,authentication
from rest_framework.response import Response
from notes.permissions import OwnerOnly
from rest_framework.views import APIView


class UserCreationView(generics.CreateAPIView):
    serializer_class=UserSerializer


class TaskCreateListView(generics.ListCreateAPIView):
    serializer_class=Taskserializer
    queryset=Task.objects.all()
    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[permissions.IsAuthenticated]


    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    
    # method overiding to filetr data acording to the users
    # def list(self, request, *args, **kwargs):
    #     qs=Task.objects.filter(owner=self.request.user)
    #     serializer_instance=Taskserializer(qs,many=True)

    #     return Response(data=serializer_instance.data)
    
    # method overiding to alter/change the query set to achive filetring the data acording to the users
    def get_queryset(self):

        qs=Task.objects.filter(owner=self.request.user)
        if "category" in self.request.query_params:
            catgeory_value=self.request.query_params.get("category")
            qs=qs.filter(category=catgeory_value)

        return qs
    

class TaskRetriveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Task.objects.all()
    serializer_class=Taskserializer
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[OwnerOnly]


class TaskSummaryApiView(APIView):

    authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request,*args,**kwargs):

        qs=Task.objects.filter(owner=request.user)
        category_summary=qs.values("category").annotate(count=Count("category"))
        status_summary=qs.values("status").annotate(count=Count("status"))
        priority_summary=qs.values("priority").annotate(count=Count("priority"))
        task_count=qs.values("title").count()

        context={
            "category_summary":category_summary,
            "status_summary":status_summary,
            "priority_summary":priority_summary,
            "task_count":task_count
        }
        print(context)

        return Response(data=context)
    

class CategoriesView(APIView):

    def get(self,request,*args,**kwargs):

        qs=Task.category_choices

        # cat=set()
        # for cats in qs:
        #     for c in cats:
        #         cat.add(c)   

        # in other way

        cat={cat for tp in qs for cat in tp}


        return Response(data={"categories":cat})
