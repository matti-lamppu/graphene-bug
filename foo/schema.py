import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from rest_framework import serializers

from .models import Foo


class FooSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foo
        fields = [
            "type",
        ]


class FooMutation(SerializerMutation):
    class Meta:
        serializer_class = FooSerializer


class Mutation(graphene.ObjectType):
    foo = FooMutation.Field()


schema = graphene.Schema(mutation=Mutation)
