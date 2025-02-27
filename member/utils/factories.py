import factory
from core.models import *
from faker import Faker

fake = Faker()


class ContactTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactTypeChoice

    name = fake.name()


class EmailTypeChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTypeChoice

    name = fake.name()


class AddressTypeChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AddressTypeChoice

    name = fake.name()


class SpouseStatusChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpouseStatusChoice
    name = factory.LazyAttribute(lambda _: fake.unique.word())


class DescendantRelationChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DescendantRelationChoice
    name = factory.LazyAttribute(lambda _: fake.unique.word())
