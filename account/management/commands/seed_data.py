from django.core.management.base import BaseCommand
from django.db import transaction
from random import choice

from member.utils.factories import *
from member.models import *
from core.models import *


class Command(BaseCommand):
    help = 'Seed full dataset'

    def handle(self, *args, **options):
        self.stdout.write('Starting full seed...')

        # Create & save choice models
        genders = GenderFactory.create_batch(3)
        membership_types = MembershipTypeFactory.create_batch(3)
        institutes = InstituteNameFactory.create_batch(3)
        membership_statuses = MembershipStatusChoiceFactory.create_batch(3)
        marital_statuses = MaritalStatusChoiceFactory.create_batch(3)
        contact_types = ContactTypeFactory.create_batch(3)
        email_types = EmailTypeChoiceFactory.create_batch(3)
        address_types = AddressTypeChoiceFactory.create_batch(3)
        spouse_statuses = SpouseStatusChoiceFactory.create_batch(3)
        descendant_relations = DescendantRelationChoiceFactory.create_batch(3)
        document_types = DocumentTypeChoiceFactory.create_batch(3)

        Gender.objects.bulk_create(genders, ignore_conflicts=True)
        MembershipType.objects.bulk_create(
            membership_types, ignore_conflicts=True)
        InstituteName.objects.bulk_create(institutes, ignore_conflicts=True)
        MembershipStatusChoice.objects.bulk_create(
            membership_statuses, ignore_conflicts=True)
        MaritalStatusChoice.objects.bulk_create(
            marital_statuses, ignore_conflicts=True)
        ContactTypeChoice.objects.bulk_create(
            contact_types, ignore_conflicts=True)
        EmailTypeChoice.objects.bulk_create(email_types, ignore_conflicts=True)
        AddressTypeChoice.objects.bulk_create(
            address_types, ignore_conflicts=True)
        SpouseStatusChoice.objects.bulk_create(
            spouse_statuses, ignore_conflicts=True)
        DescendantRelationChoice.objects.bulk_create(
            descendant_relations, ignore_conflicts=True)
        DocumentTypeChoice.objects.bulk_create(
            document_types, ignore_conflicts=True)

        # Reload saved choice objects with ids
        genders = list(Gender.objects.all())
        membership_types = list(MembershipType.objects.all())
        institutes = list(InstituteName.objects.all())
        membership_statuses = list(MembershipStatusChoice.objects.all())
        marital_statuses = list(MaritalStatusChoice.objects.all())
        contact_types = list(ContactTypeChoice.objects.all())
        email_types = list(EmailTypeChoice.objects.all())
        address_types = list(AddressTypeChoice.objects.all())
        spouse_statuses = list(SpouseStatusChoice.objects.all())
        descendant_relations = list(DescendantRelationChoice.objects.all())
        document_types = list(DocumentTypeChoice.objects.all())

        # Create 1000 members (using the saved choice objects)
        members = []
        for i in range(1000):
            members.append(Member(
                membership_type=membership_types[i % len(membership_types)],
                gender=genders[i % len(genders)],
                institute_name=institutes[i % len(institutes)],
                membership_status=membership_statuses[i % len(
                    membership_statuses)],
                marital_status=marital_statuses[i % len(marital_statuses)],
                member_ID=f"{membership_types[i % len(membership_types)].name[:9]}{i}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(
                    minimum_age=18, maximum_age=60),
                batch_number=fake.random_digit(),
                anniversary_date=fake.date_this_century(
                    before_today=True, after_today=False),
                blood_group=['A+', 'B+', 'O+', 'AB-', 'UNKNOWN'][i % 5],
                nationality=['Bangladesh', 'India'][i % 2],
                status=0,
                is_active=True,
                created_at=date.today(),
                updated_at=date.today(),
            ))

        Member.objects.bulk_create(members, batch_size=500)

        # Reload members from DB with ids
        members = list(Member.objects.all()[:1000])

        # Now create all related models for each member
        spouses = []
        descendants = []
        companions = []
        documents = []
        certificates = []
        contact_numbers = []
        emails = []
        addresses = []
        emergency_contacts = []
        jobs = []
        special_days = []

        for idx, member in enumerate(members):
            # Each related instance references the existing member & appropriate choice instances
            spouses.append(SpouseFactory.build(
                member=member,
                current_status=spouse_statuses[idx % len(spouse_statuses)]
            ))
            descendants.append(DescendantFactory.build(
                member=member,
                relation_type=descendant_relations[idx % len(
                    descendant_relations)]
            ))
            companions.append(CompanionInformationFactory.build(member=member))
            documents.append(DocumentsFactory.build(
                member=member,
                document_type=document_types[idx % len(document_types)]
            ))
            certificates.append(CertificateFactory.build(member=member))
            contact_numbers.append(ContactNumberFactory.build(
                member=member,
                contact_type=contact_types[idx % len(contact_types)]
            ))
            emails.append(EmailFactory.build(
                member=member,
                email_type=email_types[idx % len(email_types)]
            ))
            addresses.append(AddressFactory.build(
                member=member,
                address_type=address_types[idx % len(address_types)]
            ))
            emergency_contacts.append(
                EmergencyContactFactory.build(member=member))
            jobs.append(JobFactory.build(member=member))
            special_days.append(SpecialDayFactory.build(member=member))

        # Bulk create all related models (adjust batch_size as needed)
        Spouse.objects.bulk_create(spouses, batch_size=500)
        Descendant.objects.bulk_create(descendants, batch_size=500)
        CompanionInformation.objects.bulk_create(companions, batch_size=500)
        Documents.objects.bulk_create(documents, batch_size=500)
        Certificate.objects.bulk_create(certificates, batch_size=500)
        ContactNumber.objects.bulk_create(contact_numbers, batch_size=500)
        Email.objects.bulk_create(emails, batch_size=500)
        Address.objects.bulk_create(addresses, batch_size=500)
        EmergencyContact.objects.bulk_create(
            emergency_contacts, batch_size=500)
        Profession.objects.bulk_create(jobs, batch_size=500)
        SpecialDay.objects.bulk_create(special_days, batch_size=500)

        self.stdout.write('Full seeding complete! 🎉')
