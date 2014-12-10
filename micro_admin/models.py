from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import datetime


GENDER_TYPES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

USER_ROLES = (
        ('BranchManager','BranchManager'),
        ('LoanOfficer', 'LoanOfficer'),
        ('Cashier', 'Cashier')
    )

CLIENT_ROLES = (
        ('FirstLeader','FirstLeader'),
        ('SecondLeader', 'SecondLeader'),
        ('GroupMember', 'GroupMember')
    )

ACCOUNT_STATUS = (
        ('Applied', 'Applied'),
        ('Withdrawn', 'Withdrawn'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Closed', 'Closed'),
    )


INTEREST_TYPES = (
        ('Flat', 'Flat'),
        ('Declining', 'Declining'),
    )

RECEIPT_TYPES = (
        ('EntranceFee', 'EntranceFee'),
        ('MembershipFee', 'MembershipFee'),
        ('BookFee', 'BookFee'),
        ('LoanProcessingFee', 'LoanProcessingFee'),
        ('SavingsDeposit', 'SavingsDeposit'),
        ('FixedDeposit', 'FixedDeposit'),
        ('RecurringDeposit', 'RecurringDeposit'),
        ('AdditionalSavings', 'AdditionalSavings'),
        ('ShareCapital', 'ShareCapital'),
        ('PeenalInterest', 'PeenalInterest'),
        ('LoanDeposit', 'LoanDeposit'),
        ('Insurance', 'Insurance'),
    )

FD_RD_STATUS = (
       ('Opened', 'Opened'),
       ('Closed', 'Closed'),
   )

PAYMENT_TYPES = (
        ('Loans', 'Loans'),
        ('TravellingAllowance', 'TravellingAllowance'),
        ('Paymentofsalary', 'Paymentofsalary'),
        ('PrintingCharges', 'PrintingCharges'),
        ('StationaryCharges', 'StationaryCharges'),
        ('OtherCharges', 'OtherCharges'),
        ('SavingsWithdrawal', 'SavingsWithdrawal'),
        ('FixedWithdrawal', 'FixedWithdrawal'),
        ('RecurringWithdrawal', 'RecurringWithdrawal'),
    )


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    opening_date = models.DateField()
    #location = models.TextField(max_length=100)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=150)
    phone_number = models.IntegerField()
    pincode = models.IntegerField()
    is_active = models.BooleanField(default=True)


class UserManager(BaseUserManager):
    def create_user(self, username, email, branch=None, password=None):

        if not username:
            raise ValueError('Users must have an username')
        user = self.model(username=username)
        user.set_password(password)
        user.email = email
        user.branch = branch
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, branch=None):

        user = self.create_user(username, email="", password=password)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True)
    gender = models.CharField(choices = GENDER_TYPES ,max_length = 10)
    branch = models.ForeignKey(Branch,null=True,blank=True)
    user_roles = models.CharField(choices= USER_ROLES, max_length=20)
    date_of_birth = models.DateField(default='2000-01-01', null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    country = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    district = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    area = models.CharField(max_length=150, null=True)
    mobile = models.CharField(max_length=10, default='0', null=True)
    pincode = models.CharField(default='', max_length=10, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def __unicode__(self):
        return self.username


class Client(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, null=True)
    created_by = models.ForeignKey(User)
    account_number = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=10, default=True, null=True)
    gender = models.CharField(choices = GENDER_TYPES , max_length=10)
    client_role = models.CharField(choices=CLIENT_ROLES, max_length=20)
    occupation = models.CharField(max_length=200)
    annual_income = models.BigIntegerField()
    joined_date = models.DateField()
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20,default=True, null=True)
    pincode = models.CharField(max_length=20,default=True, null=True)
    photo = models.ImageField(upload_to=settings.PHOTO_PATH, null=True)
    signature = models.ImageField(upload_to =settings.SIGNATURE_PATH, null=True)
    is_active = models.BooleanField(default=True)
    branch = models.ForeignKey(Branch)
    status = models.CharField(max_length=50, default="UnAssigned", null=True)
    sharecapital_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    entrancefee_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    membershipfee_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    bookfee_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    insurance_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)


class Group(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_by = models.ForeignKey(User, related_name="group_created_by")
    account_number = models.CharField(max_length=50, unique=True)
    activation_date = models.DateField()
    is_active = models.BooleanField(default=True)
    branch = models.ForeignKey(Branch)
    staff = models.ForeignKey(User, null=True, blank=True)
    clients = models.ManyToManyField(Client, null=True, blank=True)
    status = models.CharField(max_length=50, default="UnAssigned")


class Centers(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_date = models.DateField()
    is_active = models.BooleanField(default=True)
    branch = models.ForeignKey(Branch)
    groups = models.ManyToManyField(Group, null=True,blank=True)


class GroupMeetings(models.Model):
    meeting_date = models.DateField()
    meeting_time = models.CharField(max_length=20)
    group = models.ForeignKey(Group)


class SavingsAccount(models.Model):
    account_no = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)
    created_by = models.ForeignKey(User)
    status = models.CharField(choices=ACCOUNT_STATUS, max_length=20)
    opening_date = models.DateField()
    min_required_balance = models.DecimalField(max_digits=5, decimal_places=2)
    savings_balance = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_deposits = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    total_withdrawals = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    fixeddeposit_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    fixeddepositperiod = models.IntegerField(null=True, blank=True)
    recurringdeposit_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    recurringdepositperiod = models.IntegerField(null=True, blank=True)


class LoanAccount(models.Model):
    account_no = models.CharField(max_length=50, unique=True)
    interest_type = models.CharField(choices=INTEREST_TYPES, max_length=20)
    client = models.ForeignKey(Client, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)
    created_by = models.ForeignKey(User)
    status = models.CharField(choices=ACCOUNT_STATUS, max_length=20)
    opening_date = models.DateField(auto_now_add=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    loan_issued_date = models.DateField(null=True, blank=True)
    loan_issued_by = models.ForeignKey(User, null=True, blank=True, related_name="loan_issued_by")
    closed_date = models.DateField(null=True, blank=True)
    loan_amount = models.DecimalField(max_digits=19, decimal_places=6)
    loan_repayment_period = models.IntegerField()
    loan_repayment_every = models.IntegerField()
    loan_repayment_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    total_loan_amount_repaid = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    loanpurpose_description = models.TextField()
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    interest_charged = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    total_interest_repaid = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    total_loan_paid = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    total_loan_balance = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    loanprocessingfee_amount = models.DecimalField(max_digits=19, decimal_places=6, default=0)
    no_of_repayments_completed = models.IntegerField(default=0)


class Receipts(models.Model):
    date = models.DateField()
    branch = models.ForeignKey(Branch)
    receipt_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True,default=0)
    name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    sharecapital_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    entrancefee_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    membershipfee_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    bookfee_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    loanprocessingfee_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    savingsdeposit_thrift_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    fixeddeposit_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    recurringdeposit_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    loanprinciple_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    loaninterest_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    insurance_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    staff = models.ForeignKey(User)
    savings_balance_atinstant = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    demand_loanprinciple_amount_atinstant = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    demand_loaninterest_amount_atinstant = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    principle_loan_balance_atinstant = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)


class FixedDeposits(models.Model):
    client = models.ForeignKey(Client)
    savings_account = models.ForeignKey(SavingsAccount)
    deposited_date = models.DateField()
    status = models.CharField(choices=FD_RD_STATUS, max_length=20)
    fixed_deposit_number = models.CharField(max_length=50, unique=True)
    fixed_deposit_amount = models.DecimalField(max_digits=19, decimal_places=6)
    fixed_deposit_period = models.IntegerField()
    fixed_deposit_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    nominee_firstname = models.CharField(max_length=50, null=True, blank=True)
    nominee_lastname = models.CharField(max_length=50, null=True, blank=True)
    nominee_gender = models.CharField(choices = GENDER_TYPES , max_length=10)
    relationship_with_nominee = models.CharField(max_length=50, null=True, blank=True)
    nominee_date_of_birth = models.DateField()
    nominee_occupation = models.CharField(max_length=50, null=True, blank=True)
    fixed_deposit_interest = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    maturity_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)


class RecurringDeposits(models.Model):
    client = models.ForeignKey(Client)
    savings_account = models.ForeignKey(SavingsAccount)
    deposited_date = models.DateField()
    reccuring_deposit_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(choices=FD_RD_STATUS, max_length=20)
    recurring_deposit_amount = models.DecimalField(max_digits=19, decimal_places=6)
    recurring_deposit_period = models.IntegerField()
    recurring_deposit_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    nominee_firstname = models.CharField(max_length=50, null=True, blank=True)
    nominee_lastname = models.CharField(max_length=50, null=True, blank=True)
    nominee_gender = models.CharField(choices = GENDER_TYPES , max_length=10)
    relationship_with_nominee = models.CharField(max_length=50, null=True, blank=True)
    nominee_date_of_birth = models.DateField()
    nominee_occupation = models.CharField(max_length=50, null=True, blank=True)
    recurring_deposit_interest = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)
    maturity_amount = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True)


class Payments(models.Model):
    date = models.DateField()
    branch = models.ForeignKey(Branch)
    voucher_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)
    staff = models.ForeignKey(User, null=True, blank=True)
    payment_type = models.CharField(choices = PAYMENT_TYPES , max_length=25)
    amount = models.DecimalField(max_digits=19, decimal_places=6)
    interest = models.DecimalField(max_digits=19, decimal_places=6, null=True, blank=True, default=0)
    total_amount = models.DecimalField(max_digits=19, decimal_places=6)
    totalamount_in_words = models.CharField(max_length=200)