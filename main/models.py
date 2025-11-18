from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Guardian(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=20)
    ipv4_on_activation = models.GenericIPAddressField(blank=True, null=True)
    time_on_activation = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class Child(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    dob = models.DateField(default=timezone.now)
    guardian = models.ForeignKey(to=Guardian, on_delete=models.CASCADE)
    days_to_be_contracted = models.JSONField(max_length=255, default=list)
    contract_start_date = models.DateField(default=timezone.now)

    def get_contracted_start_date_display(self):
        return self.contract_start_date.strftime('%d/%m/%Y')

    def get_contracted_days_display(self):
        """Return contracted days as human-readable string."""
        days_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if not self.days_to_be_contracted:
            return "No contracted days"
        return ", ".join(days_map[d] for d in self.days_to_be_contracted if 0 <= d < 7)


    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ChildmindingContract(models.Model):
    child = models.OneToOneField(  # one child can only have one active contract
        Child,
        on_delete=models.CASCADE,
        related_name="contract"
    )

    # Parental responsibility
    parent1_name = models.CharField(max_length=255)
    parent1_address = models.TextField()
    parent1_telephone_home = models.CharField(max_length=20, blank=True, null=True)
    parent1_telephone_work = models.CharField(max_length=20, blank=True, null=True)
    parent1_telephone_mobile = models.CharField(max_length=20, blank=True, null=True)

    parent2_name = models.CharField(max_length=255, blank=True, null=True)
    parent2_address = models.TextField(blank=True, null=True)
    parent2_telephone_home = models.CharField(max_length=20, blank=True, null=True)
    parent2_telephone_work = models.CharField(max_length=20, blank=True, null=True)
    parent2_telephone_mobile = models.CharField(max_length=20, blank=True, null=True)

    # Optional additional contact with legal rights (could be N/A)
    legal_contact = models.TextField(blank=True, null=True)

    # Collectors
    authorised_collectors = models.TextField(
        help_text="List authorised collectors with addresses and phone numbers"
    )
    collection_password = models.CharField(max_length=255)

    # Fees and conditions
    day_fee_gbp = models.IntegerField()

    # Contract details
    start_date = models.DateField()

    # Agreement
    parent_signature = models.CharField(max_length=255)
    parent_signed_at = models.DateTimeField(auto_now_add=True)
    parent_ip = models.GenericIPAddressField(blank=True, null=True)

    childminder_signature = models.CharField(max_length=255, default="Laura Oldfield")
    childminder_signed_at = models.DateTimeField(auto_now_add=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Childminding Contract"
        verbose_name_plural = "Childminding Contracts"

    def __str__(self):
        return f"Contract for {self.child} ({self.start_date})"


class ConsentForm(models.Model):
    child = models.OneToOneField(
        Child,
        on_delete=models.CASCADE,
        related_name="consent"
    )

    # Parent/guardian consents
    policies_signature = models.CharField(max_length=255)
    complaints_signature = models.CharField(max_length=255)
    emergency_signature = models.CharField(max_length=255)
    emergency_caregiver_signature = models.CharField(max_length=255)
    outings_signature = models.CharField(max_length=255)
    photos_signature = models.CharField(max_length=255)
    transport_signature = models.CharField(max_length=255)
    equipment_signature = models.CharField(max_length=255)
    firstaid_signature = models.CharField(max_length=255)
    sharing_signature = models.CharField(max_length=255)
    plaster_signature = models.CharField(max_length=255)
    suncream_wipes_signature = models.CharField(max_length=255)
    calpol_signature = models.CharField(max_length=255)

    # Metadata for signing
    parent_signature = models.CharField(max_length=255)
    parent_signed_at = models.DateTimeField(auto_now_add=True)
    parent_ip = models.GenericIPAddressField(blank=True, null=True)

    # Childminder acknowledgment
    childminder_signature = models.CharField(max_length=255, default="Laura Oldfield")
    childminder_signed_at = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Consent Form"
        verbose_name_plural = "Consent Forms"

    def __str__(self):
        return f"Consent Form for {self.child}"
    

class ChildRecord(models.Model):
    child = models.OneToOneField(
        Child,
        on_delete=models.CASCADE,
        related_name="record"
    )

    # Core child details
    home_address = models.TextField()
    languages_spoken = models.CharField(
        max_length=255,
        help_text="List main language(s) spoken at home"
    )
    religion_cultural_needs = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional (e.g. dietary or cultural practices)"
    )

    # Health details
    doctor_name = models.CharField(max_length=255)
    doctor_surgery = models.CharField(max_length=255)
    doctor_phone = models.CharField(max_length=20)

    medical_conditions = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    dietary_needs = models.TextField(blank=True, null=True)
    medication = models.TextField(blank=True, null=True)
    vaccinations = models.TextField(
        blank=True,
        null=True,
        help_text="Optional: vaccination record/confirmation"
    )

    # Emergency contacts (extra adults beyond parents/guardians)
    emergency_contact1_name = models.CharField(max_length=255)
    emergency_contact1_relationship = models.CharField(max_length=255)
    emergency_contact1_phone = models.CharField(max_length=20)

    emergency_contact2_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact2_relationship = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact2_phone = models.CharField(max_length=20, blank=True, null=True)

    # Additional notes from parents
    additional_notes = models.TextField(
        blank=True,
        null=True,
        help_text="E.g. sleep routines, comfort items, likes/dislikes"
    )

    # Metadata for signing
    parent_signature = models.CharField(max_length=255)
    parent_signed_at = models.DateTimeField(auto_now_add=True)
    parent_ip = models.GenericIPAddressField(blank=True, null=True)

    # Childminder acknowledgment
    childminder_signature = models.CharField(max_length=255, default="Laura Oldfield")
    childminder_signed_at = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Child Record for {self.child}"


class DailyRegister(models.Model):
    child = models.ForeignKey(to=Child, on_delete=models.CASCADE)
    clock_in = models.DateTimeField(auto_now_add=True)
    clock_out = models.DateTimeField(blank=True, null=True, default=None)