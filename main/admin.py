from django.contrib import admin
from .models import (
    Guardian, Child, ChildmindingContract,
    ConsentForm, ChildRecord, DailyRegister
)

# --------------------------
# Guardian Admin
# --------------------------
@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ("user", "telephone", "ipv4_on_activation", "time_on_activation")
    search_fields = ("user__first_name", "user__last_name", "telephone")
    list_filter = ("time_on_activation",)
    readonly_fields = ("ipv4_on_activation", "time_on_activation")


# --------------------------
# Inlines for Child details
# --------------------------
class ChildmindingContractInline(admin.StackedInline):
    model = ChildmindingContract
    can_delete = False
    extra = 0
    readonly_fields = ("parent_signed_at", "childminder_signed_at", "parent_ip")


class ConsentFormInline(admin.StackedInline):
    model = ConsentForm
    can_delete = False
    extra = 0
    readonly_fields = ("parent_signed_at", "childminder_signed_at", "parent_ip")


class ChildRecordInline(admin.StackedInline):
    model = ChildRecord
    can_delete = False
    extra = 0
    readonly_fields = ("parent_signed_at", "childminder_signed_at", "parent_ip")


# --------------------------
# Child Admin
# --------------------------
@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = (
        "first_name", "last_name",
        "guardian",
        "dob",
        "get_contracted_days_display",
        "get_contracted_start_date_display",
    )
    search_fields = ("first_name", "last_name", "guardian__user__first_name")
    list_filter = ("contract_start_date", "guardian")
    
    inlines = [
        ChildmindingContractInline,
        ConsentFormInline,
        ChildRecordInline,
    ]


# --------------------------
# Childminding Contract Admin
# --------------------------
@admin.register(ChildmindingContract)
class ChildmindingContractAdmin(admin.ModelAdmin):
    list_display = ("child", "start_date", "day_fee_gbp", "parent_signed_at")
    search_fields = ("child__first_name", "child__last_name", "parent1_name")
    list_filter = ("start_date",)
    readonly_fields = (
        "parent_signed_at", "childminder_signed_at",
        "parent_ip", "created_at", "updated_at"
    )


# --------------------------
# Consent Form Admin
# --------------------------
@admin.register(ConsentForm)
class ConsentFormAdmin(admin.ModelAdmin):
    list_display = ("child", "parent_signed_at")
    search_fields = ("child__first_name", "child__last_name")
    readonly_fields = (
        "parent_signed_at", "childminder_signed_at",
        "parent_ip", "created_at", "updated_at"
    )


# --------------------------
# Child Record Admin
# --------------------------
@admin.register(ChildRecord)
class ChildRecordAdmin(admin.ModelAdmin):
    list_display = ("child", "doctor_name", "doctor_phone")
    search_fields = ("child__first_name", "child__last_name", "doctor_name")
    readonly_fields = (
        "parent_signed_at", "childminder_signed_at",
        "parent_ip", "created_at", "updated_at"
    )


# --------------------------
# Daily Register Admin
# --------------------------
@admin.register(DailyRegister)
class DailyRegisterAdmin(admin.ModelAdmin):
    list_display = ("child", "clock_in", "clock_out")
    list_filter = ("clock_in", "clock_out")
    search_fields = ("child__first_name", "child__last_name")
