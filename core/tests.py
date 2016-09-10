from django.test import TestCase
from core.forms import *
from micro_admin.models import *
from django.core.urlresolvers import reverse
from tempfile import NamedTemporaryFile


class Modelform_test(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'jag123', 'jagadeesh123@gmail.com')
        self.branch = Branch.objects.create(
            name='sbh', opening_date='2014-10-10', country='ind', state='AP',
            district='Nellore', city='Nellore', area='circle', pincode=502286,
            phone_number=944454651165)
        self.client = Client.objects.create(
            first_name="client1", last_name="MicroPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=1, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')

        self.client1 = Client.objects.create(
            first_name="client", last_name="MicroPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=2, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')

        self.memberloan = LoanAccount.objects.create(
            account_no='CL1', interest_type='Flat', client=self.client,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2014-1-1')

        self.group1 = Group.objects.create(
            name='group1', created_by=self.user, account_number='123',
            activation_date='2014-1-1', branch=self.branch)
        self.group1.clients.add(self.client)
        self.group1.save()

        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='1234',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.client1)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL1', interest_type='Flat', group=self.group1,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2,
            interest_charged=20, total_loan_balance=12000,
            group_loan_account=self.grouploan, client=self.client)
        self.fixed_deposit = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f1', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        self.recurring_deposit = RecurringDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1',
            reccuring_deposit_number='r1', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        self.payments = Payments.objects.create(
            date="2015-2-20", staff=self.user, branch=self.branch,
            client=self.client, payment_type="OtherCharges", voucher_number=1,
            amount=100, total_amount=101, interest=1,
            totalamount_in_words="hundred", loan_account=self.memberloan)
        self.client_savings_account = SavingsAccount.objects.create(
            account_no='CS1', client=self.client, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=10000,
            annual_interest_rate=1, created_by=self.user, status='Approved')

        self.group1_savings_account = SavingsAccount.objects.create(
            account_no='GS1', group=self.group1, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=10000,
            annual_interest_rate=1, created_by=self.user, status='Approved')

        self.fixed_deposits123 = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f2221', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2016-08-30', nominee_occupation='teacher')
        
        self.temp_file = NamedTemporaryFile(delete=False, suffix='.jpg',)

    def test_ClientLoanAccountsForm(self):
        form = ClientLoanAccountsForm(data={
            'name': 'client1', 'account_number': 1})
        self.assertTrue(form.is_valid())

    def test_ClientLoanAccountsForm_invalid(self):
        form = ClientLoanAccountsForm(data={
            'name': self.client.first_name, 'account_number': 83})
        self.assertFalse(form.is_valid())

    def test_GetLoanDemandsForm(self):
        form = GetLoanDemandsForm(data={
            'name': self.client.first_name, 'loan_account_no': self.memberloan.account_no})
        self.assertTrue(form.is_valid())

    def test_GetLoanDemandsForm_invalid(self):
        form = GetLoanDemandsForm(data={
            'name': self.client.first_name, 'loan_account_no': ''})
        self.assertFalse(form.is_valid())

    def test_GetLoanDemandsForm1(self):
        form = GetLoanDemandsForm(data={
            'name': self.client.first_name, 'loan_account_no': self.memberloan.account_no, 'group_loan_account_no': 11})
        self.assertFalse(form.is_valid())

    def test_GetLoanDemandsForm_invalid1(self):
        form = GetLoanDemandsForm(data={
            'name': self.client.first_name, 'group_loan_account_no': self.grouploan.account_no})
        self.assertTrue(form.is_valid())

    def test_GetFixedDepositsForm(self):
        form = GetFixedDepositsForm(data={'fixed_deposit_account_no': self.fixed_deposit.fixed_deposit_number})
        self.assertTrue(form.is_valid())

    def test_GetFixedDepositsForm1(self):
        self.fixed_deposit1 = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Paid',
            fixed_deposit_number='f2', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        form = GetFixedDepositsForm(data={'fixed_deposit_account_no': self.fixed_deposit1.fixed_deposit_number})
        self.assertFalse(form.is_valid())

    def test_GetFixedDepositsForm2(self):
        self.fixed_deposit2 = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Closed',
            fixed_deposit_number='f3', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        form = GetFixedDepositsForm(data={'fixed_deposit_account_no': self.fixed_deposit2.fixed_deposit_number})
        self.assertFalse(form.is_valid())

    def test_GetFixedDepositsForm3(self):
        form = GetFixedDepositsForm(data={'fixed_deposit_account_no': '123'})
        self.assertFalse(form.is_valid())

    def test_GetRecurringDepositsForm(self):
        form = GetRecurringDepositsForm(data={'recurring_deposit_account_no': self.recurring_deposit.reccuring_deposit_number})
        self.assertTrue(form.is_valid())

    def test_GetRecurringDepositsForm1(self):
        self.recurring_deposit1 = RecurringDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1',
            reccuring_deposit_number='r2', status='Paid',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        form = GetRecurringDepositsForm(data={'recurring_deposit_account_no': self.recurring_deposit1.reccuring_deposit_number})
        self.assertFalse(form.is_valid())

    def test_GetRecurringDepositsForm2(self):
        self.recurring_deposit2 = RecurringDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1',
            reccuring_deposit_number='r3', status='Closed',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        form = GetRecurringDepositsForm(data={'recurring_deposit_account_no': self.recurring_deposit2.reccuring_deposit_number})
        self.assertFalse(form.is_valid())

    def test_GetRecurringDepositsForm3(self):
        form = GetRecurringDepositsForm(data={'recurring_deposit_account_no': '123'})
        self.assertFalse(form.is_valid())

    def test_ClientDepositsAccountsForm(self):
        form = ClientDepositsAccountsForm(data={'payment_type': '123', 'client_name': self.client.first_name, 'client_account_number': 1})
        self.assertTrue(form.is_valid())

    def test_ClientDepositsAccountsForm1(self):
        form = ClientDepositsAccountsForm(data={'payment_type': '123', 'client_name': '', 'client_account_number': ''})
        self.assertFalse(form.is_valid())

    def test_ClientDepositsAccountsForm2(self):
        form = ClientDepositsAccountsForm(data={'payment_type': '123', 'client_name': 'cc1', 'client_account_number': 1})
        self.assertFalse(form.is_valid())

    def test_GetFixedDepositsPaidForm(self):
        form = GetFixedDepositsPaidForm(data={'fixed_deposit_account_no': 'gh'}, initial={'client': self.client})
        self.assertFalse(form.is_valid())

    def test_GetFixedDepositsPaidForm2(self):
        self.fixed_deposit22 = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Closed',
            fixed_deposit_number='f22', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        form = GetFixedDepositsPaidForm(data={'fixed_deposit_account_no': self.fixed_deposit22.fixed_deposit_number}, initial={'client': self.client})
        self.assertFalse(form.is_valid())

    def test_GetFixedDepositsPaidForm3(self):
        self.fixed_deposit21 = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f222', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        form = GetFixedDepositsPaidForm(data={'fixed_deposit_account_no': self.fixed_deposit21.fixed_deposit_number}, initial={'client': self.client})
        self.assertFalse(form.is_valid())

    def test_GetRecurringDepositsPaidForm(self):
        form = GetRecurringDepositsPaidForm(data={'recurring_deposit_account_no': 'gh'}, initial={'client': self.client})
        self.assertFalse(form.is_valid())

    def test_GetRecurringDepositsPaidForm2(self):
        self.recurring_deposit22 = RecurringDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1',
            reccuring_deposit_number='r22', status='Closed',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        form = GetRecurringDepositsPaidForm(data={'recurring_deposit_account_no': self.recurring_deposit22.reccuring_deposit_number}, initial={'client': self.client})
        self.assertFalse(form.is_valid())

    def test_PaymentForm(self):
        form = PaymentForm(data={
            "date": '10/10/2014', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 500,
            "interest": 3, "total_amount": 5000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'member_loan_account_no': self.memberloan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm1(self):
        form = PaymentForm(data={
            "date": '10/10/2014', "branch": self.branch.id,
            "voucher_number": self.payments.voucher_number, "payment_type": 'Loans', "amount": 0,
            "interest": 3, "total_amount": 0,
            "totalamount_in_words": '1 rupee', 'client_name': self.client, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm2(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Paymentofsalary', "amount": 100,
            "interest": 3, "total_amount": 100,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': None, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm3(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'TravellingAllowance', "amount": 1000,
            "interest": 3, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm4(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'TravellingAllowance', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': 'qq', 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm5(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'PrintingCharges', "amount": 1000,
            "interest": 3, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm6(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'PrintingCharges', "amount": 1000,
            "interest": None, "total_amount": 100,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm7(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 100,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm8(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": '100', "total_amount": 100,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm9(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm10(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': None,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm11(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertTrue(form.is_valid())

    def test_PaymentForm12(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': 'fgx', 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm13(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client1.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id, 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number})
        self.assertFalse(form.is_valid())

    def test_PaymentForm14(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id, 'group_name': self.group1.name,
            'group_account_number': '4567890'})
        self.assertFalse(form.is_valid())

    def test_PaymentForm15(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id, 'group_name': self.group1.name,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm16(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id, 'group_name': 'fguj',
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm17(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id, 'group_name': self.group1.name,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm19(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 100,
            "interest": None, "total_amount": 100,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id, 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number})
        self.assertTrue(form.is_valid())

    def test_PaymentForm18(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id, 'group_name': 'gfdd',
            'group_account_number': '67'})
        self.assertFalse(form.is_valid())

    def test_PaymentForm20(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm21(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number})
        self.assertFalse(form.is_valid())

    def test_PaymentForm22(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm23(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm24(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': 'fghj', 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm25(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'fixed_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm26(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'fixed_deposit_account_no': self.fixed_deposit.fixed_deposit_number})
        self.assertFalse(form.is_valid())

    def test_PaymentForm27(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'fixed_deposit_account_no': '45'})
        self.assertFalse(form.is_valid())

    def test_PaymentForm28(self):
        self.fixed_deposits1 = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f123', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'FixedWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'fixed_deposit_account_no': self.fixed_deposits1.fixed_deposit_number})
        self.assertFalse(form.is_valid())

    def test_PaymentForm29(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'RecurringWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm30(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'RecurringWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': self.group1.name,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm31(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'RecurringWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm51(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'RecurringWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm52(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'RecurringWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': 'dfghj', 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm32(self):
        self.recurring_deposit1 = RecurringDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1',
            reccuring_deposit_number='r11', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend', number_of_payments=0,
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'RecurringWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'recurring_deposit_account_no': self.recurring_deposit1.reccuring_deposit_number})
        self.assertFalse(form.is_valid())

    def test_PaymentForm33(self):
        self.recurring_deposit1 = RecurringDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1',
            reccuring_deposit_number='r12', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend', number_of_payments=1,
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'RecurringWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'recurring_deposit_account_no': self.recurring_deposit1.reccuring_deposit_number})
        self.assertFalse(form.is_valid())

    def test_PaymentForm34(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": 12, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm35(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm36(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': self.group1.name,
            'group_account_number': None, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm37(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': self.group1.name,
            'group_account_number': None, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm38(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm39(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': 'fghj',
            'group_account_number': self.group1.account_number, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm40(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': '345678', 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm41(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': self.grouploan.id, 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm42(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 12000,
            "interest": None, "total_amount": 12000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': self.grouploan.id, 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number, 'recurring_deposit_account_no': None})
        self.assertTrue(form.is_valid())

    def test_PaymentForm43(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 1200,
            "interest": None, "total_amount": 120000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': self.grouploan.id, 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm44(self):
        self.group3 = Group.objects.create(
            name='group3', created_by=self.user, account_number='1231',
            activation_date='2014-1-1', branch=self.branch)

        self.grouploan1 = LoanAccount.objects.create(
            account_no='GL11', interest_type='Flat', group=self.group3,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 12000,
            "interest": None, "total_amount": 12000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': self.grouploan1.id, 'group_name': self.group3.name,
            'group_account_number': self.group3.account_number, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm45(self):
        self.group4 = Group.objects.create(
            name='group4', created_by=self.user, account_number='4',
            activation_date='2014-1-1', branch=self.branch)

        self.grouploan4 = LoanAccount.objects.create(
            account_no='GL122', interest_type='Flat', group=self.group4,
            created_by=self.user, status="Applied", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 12000,
            "interest": None, "total_amount": 12000,
            "totalamount_in_words": '1 rupee', 'client_name': None, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': self.grouploan4.id, 'group_name': self.group4.name,
            'group_account_number': self.group4.account_number, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm46(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': self.group1.name,
            'group_account_number': self.group1.account_number, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm47(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': None,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm48(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm49(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': 'ghjk', 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'recurring_deposit_account_no': None})
        self.assertFalse(form.is_valid())

    def test_PaymentForm50(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 12000,
            "interest": None, "total_amount": 12000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'member_loan_account_no': '545'})
        self.assertFalse(form.is_valid())

    def test_PaymentForm55(self):
        self.client4 = Client.objects.create(
            first_name="client4", last_name="MicroPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=4, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')

        self.memberloan4 = LoanAccount.objects.create(
            account_no='CL4', interest_type='Flat', client=self.client4,
            created_by=self.user, status="Applied", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2014-1-1')
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client4.first_name, 'client_account_number': self.client4.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'member_loan_account_no': self.memberloan4.id})
        self.assertFalse(form.is_valid())

    def test_PaymentForm56(self):
        form = PaymentForm(data={
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 1000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.client.first_name, 'client_account_number': self.client.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'member_loan_account_no': self.memberloan.id})
        self.assertFalse(form.is_valid())

    # Receipts Form Tests
    def test_ReceiptForm1(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': "", "branch": self.branch.id,
             "receipt_number": 1})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm2(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': 111, "branch": self.branch.id,
             "receipt_number": 2})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm3(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id,
             "receipt_number": 2, 'sharecapital_amount': ""})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm4(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id,
             "receipt_number": 2, 'loan_account_no': '129', 'sharecapital_amount': "22"})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm5(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'loan_account_no': "", 'sharecapital_amount': "22"})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm6(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': "",
             "receipt_number": 2, 'group_name': self.group1.name, 'group_account_number': "555", 'sharecapital_amount': "22"})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm7(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': "",
             "receipt_number": 2, 'group_name': "", 'group_account_number': "555", 'sharecapital_amount': "22"})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm8(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': "",
             "receipt_number": 2, 'group_name': self.group1.name, 'group_loan_account_no': "12875", 'sharecapital_amount': "22",
             "group_account_number": self.group1.account_number})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm9(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': "",
             "receipt_number": 2, 'group_name': self.group1.name, 'group_loan_account_no': self.grouploan.account_no, 'sharecapital_amount': "22",
             "group_account_number": self.group1.account_number, 'loan_account_no': self.memberloan.account_no})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm10(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client1.first_name,
             'account_number': self.client1.account_number, "branch": self.branch.id, 'loanprinciple_amount': "",
             "receipt_number": 2, 'sharecapital_amount': "22", 'savingsdeposit_thrift_amount': 100
             })
        self.assertFalse(form.is_valid())

    # def test_ReceiptForm11(self):
    #     form = ReceiptForm(data={
    #          "date": '10/10/2014', 'name': self.client1.first_name,
    #          'account_number': self.client1.account_number, "branch": self.branch.id, 'loanprinciple_amount': "",
    #          "receipt_number": 2, 'sharecapital_amount': "22", 'savingsdeposit_thrift_amount': 100
    #          })
    #     self.assertFalse(form.is_valid())

    def test_ReceiptForm12(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Applied", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2014-1-1')

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", "loaninterest_amount": 10, 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm13(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user)

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", "loaninterest_amount": 10, 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm14(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1')

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", "loaninterest_amount": 10, 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm15(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            total_loan_balance=100)

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", "loaninterest_amount": 10, 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no, 'loanprinciple_amount': 1000})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm16(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            total_loan_balance=100, interest_charged=2)

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", "loaninterest_amount": 10, 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no, 'loanprinciple_amount': 1})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm17(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            interest_charged=2, principle_repayment=12,
            total_loan_balance=5000)

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm18(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            interest_charged=20000, principle_repayment=14000,
            total_loan_balance=5000)

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no, 'loaninterest_amount': 13000})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm19(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            interest_charged=20000, principle_repayment=14000,
            total_loan_balance=5000)

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no, 'loaninterest_amount': 1})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm20(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Rejected", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            interest_charged=20000, principle_repayment=14000,
            total_loan_balance=5000)

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no, 'loaninterest_amount': 1})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm21(self):
        self.memberloan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', client=self.client,
            created_by=self.user, status="Closed", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            interest_charged=20000, principle_repayment=14000,
            total_loan_balance=5000)

        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'group_loan_account_no': 'jg',
             "loan_account_no": self.memberloan12.account_no, 'loaninterest_amount': 1})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm22(self):
        self.grouploan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', group=self.group1,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            interest_charged=20000, principle_repayment=14000,
            total_loan_balance=5000)
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='CL112', interest_type='Flat',
            status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2,
            interest_charged=20, total_loan_balance=12000,
            group_loan_account=self.grouploan12, client=self.client)
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'group_loan_account_no': 'jg',
             'loaninterest_amount': 1, 'group_name': self.group1.name, 'group_account_number': self.group1.account_number,
             'group_loan_account_no': self.grouploan12.account_no})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm23(self):
        self.grouploan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', group=self.group1,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            interest_charged=20000, principle_repayment=14000,
            total_loan_balance=5000)
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='CL112', interest_type='Flat',
            status="Applied", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2,
            interest_charged=20, total_loan_balance=12000,
            group_loan_account=self.grouploan12, client=self.client)
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'group_loan_account_no': 'jg',
             'loaninterest_amount': 1, 'group_name': self.group1.name, 'group_account_number': self.group1.account_number,
             'group_loan_account_no': self.grouploan12.account_no})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm24(self):
        self.grouploan12 = LoanAccount.objects.create(
            account_no='CL112', interest_type='Flat', group=self.group1,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            loan_issued_by=self.user, loan_issued_date='2014-1-1',
            interest_charged=20000, principle_repayment=14000,
            total_loan_balance=5000)
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'group_loan_account_no': 'jg',
             'loaninterest_amount': 1, 'group_name': self.group1.name, 'group_account_number': self.group1.account_number,
             'group_loan_account_no': self.grouploan12.account_no})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm25(self):
        self.fixed_deposit = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f116', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'fixed_deposit_account_no': self.fixed_deposit.fixed_deposit_number,
             "loan_account_no": self.memberloan.account_no, 'fixeddeposit_amount': 1000})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm26(self):
        self.fixed_deposit = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f116', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        self.receipt1 = Receipts.objects.create(
            fixed_deposit_account=self.fixed_deposit, branch=self.branch,
            receipt_number="5", client=self.client, date="2014-1-1", staff=self.user)
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'fixed_deposit_account_no': self.fixed_deposit.fixed_deposit_number,
             "loan_account_no": self.memberloan.account_no, 'fixeddeposit_amount': 1000})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm27(self):
        self.fixed_deposit = FixedDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1', status='Closed',
            fixed_deposit_number='f116', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client.first_name,
             'account_number': self.client.account_number, "branch": self.branch.id, 'loanprinciple_amount': 1000,
             "receipt_number": 2, 'sharecapital_amount': "22", 'fixed_deposit_account_no': self.fixed_deposit.fixed_deposit_number,
             "loan_account_no": self.memberloan.account_no, 'fixeddeposit_amount': 1000})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm28(self):
        self.client1 = Client.objects.create(
            first_name="client1", last_name="MicroPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=1231, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.fixed_deposit = FixedDeposits.objects.create(
            client=self.client1, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f1161', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
       
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client1.first_name,
             'account_number': self.client1.account_number, "branch": self.branch.id,
             "receipt_number": 2, 'sharecapital_amount': "22", 'fixed_deposit_account_no': self.fixed_deposit.fixed_deposit_number,
             "loan_account_no": '', 'fixeddeposit_amount': 1000})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm29(self):
        self.client1 = Client.objects.create(
            first_name="client1", last_name="MicroPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=1231, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.fixed_deposit = FixedDeposits.objects.create(
            client=self.client1, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f1161', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
       
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client1.first_name,
             'account_number': self.client1.account_number, "branch": self.branch.id,
             "receipt_number": 2, 'sharecapital_amount': "22",
             "loan_account_no": '', 'fixeddeposit_amount': 1000})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm30(self):
        self.recurring_deposit = RecurringDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1',
            reccuring_deposit_number='r11', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client1.first_name,
             'account_number': self.client1.account_number, "branch": self.branch.id,
             "receipt_number": 2, 'sharecapital_amount': "22", 'recurring_deposit_account_no': self.recurring_deposit.reccuring_deposit_number,
             "loan_account_no": '', 'recurringdeposit_amount': 0})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm31(self):
        self.recurring_deposit = RecurringDeposits.objects.create(
            client=self.client, deposited_date='2014-1-1',
            reccuring_deposit_number='r11', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=20,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend', number_of_payments=200,
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client1.first_name,
             'account_number': self.client1.account_number, "branch": self.branch.id,
             "receipt_number": 2, 'sharecapital_amount': "22", 'recurring_deposit_account_no': self.recurring_deposit.reccuring_deposit_number,
             "loan_account_no": '', 'recurringdeposit_amount': 0})
        self.assertFalse(form.is_valid())

    def test_ReceiptForm32(self):
        form = ReceiptForm(data={
             "date": '10/10/2014', 'name': self.client1.first_name,
             'account_number': self.client1.account_number, "branch": self.branch.id,
             "receipt_number": 2, 'sharecapital_amount': "22",
             "loan_account_no": '', 'recurringdeposit_amount': 10})
        self.assertFalse(form.is_valid())


class Core_Views_test(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('jagadeesh', 'jag123')
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        self.branch = Branch.objects.create(
            name='sbh', opening_date='2014-10-10', country='ind', state='AP',
            district='Nellore', city='Nellore', area='circle', pincode=502286,
            phone_number=944454651165)
        self.member = Client.objects.create(
            first_name="Member1", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=1, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')

        self.member1 = Client.objects.create(
            first_name="Member12", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=2, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')

        self.member_savings_account = SavingsAccount.objects.create(
            account_no='CS112', client=self.member, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=10000,
            annual_interest_rate=1, created_by=self.user, status='Approved')

        self.memberloan = LoanAccount.objects.create(
            account_no='CL1', interest_type='Flat', client=self.member,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2014-1-1')
        self.memberloan1 = LoanAccount.objects.create(
            account_no='CL2', interest_type='Flat', client=self.member,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_date=None)

        self.payments = Payments.objects.create(
            date="2015-2-20", staff=self.user, branch=self.branch,
            client=self.member, payment_type="OtherCharges", voucher_number=1,
            amount=100, total_amount=101, interest=1,
            totalamount_in_words="hundred", loan_account=self.memberloan)

        self.group1 = Group.objects.create(
            name='group1', created_by=self.user, account_number='123',
            activation_date='2014-1-1', branch=self.branch)
        self.group1.clients.add(self.member)
        self.group1.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL1', interest_type='Flat', group=self.group1,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')

        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=12000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member)

        self.grouploan1 = LoanAccount.objects.create(
            account_no='GL2', interest_type='Flat', group=self.group1,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_date=None)

        self.grouploanpayments = Payments.objects.create(
            date="2015-2-20", staff=self.user, branch=self.branch,
            group=self.group1, payment_type="OtherCharges", voucher_number=2,
            amount=100, total_amount=101, interest=1,
            totalamount_in_words="hundred", loan_account=self.grouploan)
        self.fixed_deposit11 = FixedDeposits.objects.create(
            client=self.member, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f11', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        self.recurring_deposit = RecurringDeposits.objects.create(
            client=self.member, deposited_date='2014-1-1',
            reccuring_deposit_number='r1', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        self.group_savings_account = SavingsAccount.objects.create(
                account_no='GS112', group=self.group1, opening_date='2014-1-1',
                min_required_balance=0, savings_balance=10000,
                annual_interest_rate=1, created_by=self.user, status='Approved')

    def test_getmemberloanaccounts1(self):
        response = self.client.post(
            reverse("core:getmemberloanaccounts"),
            {'account_number': 1, 'name': self.member.first_name})
        self.assertEqual(response.status_code, 200)

    def test_getmemberloanaccounts_invalid(self):
        response = self.client.post(
            reverse("core:getmemberloanaccounts"),
            {'account_number': 1, 'name': ''})
        self.assertEqual(response.status_code, 200)

    def test_getloandemands_view(self):
        response = self.client.post(
            reverse("core:getloandemands"),
            {'name': self.member.first_name, 'group_loan_account_no': self.grouploan.account_no})
        self.assertEqual(response.status_code, 200)

    def test_getloandemands_view_invalid(self):
        response = self.client.post(
            reverse("core:getloandemands"),
            {'name': self.member.first_name, 'group_loan_account_no': ""})
        self.assertEqual(response.status_code, 200)

    def test_get_group_loan_accounts(self):
        response = self.client.get(
            reverse("core:get_group_loan_accounts"),
            {'group_name': self.group1.name, 'group_account_no': self.group1.account_number})
        self.assertEqual(response.status_code, 200)

    def test_get_group_loan_accounts_invalid(self):
        response = self.client.get(
            reverse("core:get_group_loan_accounts"),
            {'group_name': 'g1', 'group_account_no': self.group1.account_number})
        self.assertEqual(response.status_code, 200)

    def test_get_member_loan_accounts(self):
        response = self.client.get(
            reverse("core:get_member_loan_accounts"),
            {'client_name': self.member.first_name, 'client_account_number': self.member.account_number})
        self.assertEqual(response.status_code, 200)

    def test_get_member_loan_accounts_invalid(self):
        response = self.client.get(
            reverse("core:get_member_loan_accounts"),
            {'client_name': 'c1', 'client_account_number': self.member.account_number})
        self.assertEqual(response.status_code, 200)

    def test_GetFixedDepositAccountsView(self):
        response = self.client.post(
            reverse("core:getmemberfixeddepositaccounts"),
            {'fixed_deposit_account_no': self.fixed_deposit11.fixed_deposit_number})
        self.assertEqual(response.status_code, 200)

    def test_GetFixedDepositAccountsView_invalid(self):
        response = self.client.post(
            reverse("core:getmemberfixeddepositaccounts"),
            {'fixed_deposit_account_no': None})
        self.assertEqual(response.status_code, 200)

    def test_GetRecurringDepositAccountsView(self):
        response = self.client.post(
            reverse("core:getmemberrecurringdepositaccounts"),
            {'recurring_deposit_account_no': self.recurring_deposit.reccuring_deposit_number})
        self.assertEqual(response.status_code, 200)

    def test_GetRecurringDepositAccountsView_invalid(self):
        response = self.client.post(
            reverse("core:getmemberrecurringdepositaccounts"),
            {'recurring_deposit_account_no': None})
        self.assertEqual(response.status_code, 200)

    def test_ClientDepositAccountsView(self):
        self.fixed_deposit11 = FixedDeposits.objects.create(
            client=self.member, deposited_date='2014-1-1', status='Paid',
            fixed_deposit_number='f5', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        response = self.client.post(
            reverse("core:getmemberdepositaccounts"),
            {'payment_type': 'FixedWithdrawal', 'client_name': self.member.first_name, 'client_account_number': 1})
        self.assertEqual(response.status_code, 200)

    def test_ClientDepositAccountsView1(self):
        self.recurring_deposit = RecurringDeposits.objects.create(
            client=self.member, deposited_date='2014-1-1',
            reccuring_deposit_number='r3', status='Paid',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher', number_of_payments=1)
        response = self.client.post(
            reverse("core:getmemberdepositaccounts"),
            {'payment_type': 'RecurringWithdrawal', 'client_name': self.member.first_name, 'client_account_number': 1})
        self.assertEqual(response.status_code, 200)

    def test_ClientDepositAccountsView_invalid(self):
        
        response = self.client.post(
            reverse("core:getmemberdepositaccounts"),
            {'payment_type': None, 'client_name': None, 'client_account_number': None})
        self.assertEqual(response.status_code, 200)

    def test_GetFixedDepositPaidAccountsView(self):
        self.fixed_deposit11 = FixedDeposits.objects.create(
            client=self.member, deposited_date='2014-1-1', status='Paid',
            fixed_deposit_number='f131', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        response = self.client.post(
            reverse("core:getmemberfixeddepositpaidaccounts"),
            {'fixed_deposit_account_no': self.fixed_deposit11.fixed_deposit_number, 'client_name': self.member.first_name,
             "client_account_number": 1})
        self.assertEqual(response.status_code, 200)

    def test_GetFixedDepositPaidAccountsView_invalid(self):
        response = self.client.post(
            reverse("core:getmemberfixeddepositpaidaccounts"),
            {'fixed_deposit_account_no': None})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_invalid(self):
        self.recurring_deposit1 = RecurringDeposits.objects.create(
            client=self.member, deposited_date='2014-1-1',
            reccuring_deposit_number='r441', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend', number_of_payments=0,
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 375, "payment_type": 'RecurringWithdrawal', "amount": 10000,
            "interest": None, "total_amount": 1000,
            "totalamount_in_words": '1 rupee', 'client_name': self.member.first_name, 'client_account_number': self.member.account_number,
            'staff_username': None, 'group_loan_account_no': None, 'group_name': None,
            'group_account_number': None, 'recurring_deposit_account_no': self.recurring_deposit1.reccuring_deposit_number})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_valid1(self):
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'TravellingAllowance', "amount": 1000,
            "total_amount": 1000, "totalamount_in_words": '1 rupee', 'client_name': self.member.first_name, 'client_account_number': 1,
            'staff_username': self.user.username, 'group_loan_account_no': self.grouploan.id})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_valid2(self):
        self.member_savings_account = SavingsAccount.objects.create(
            account_no='CS321', client=self.member1, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=10000,
            annual_interest_rate=1, created_by=self.user, status='Approved')
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 897, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": 3, "total_amount": 1003,
            "totalamount_in_words": '1 rupee', 'client_name': self.member1.first_name, 'client_account_number': self.member1.account_number,
            'staff_username': self.user.username})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_valid3(self):
        self.group_savings_account = SavingsAccount.objects.create(
            account_no='CS321', group=self.group1, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=10000,
            annual_interest_rate=1, created_by=self.user, status='Approved')
        self.member_savings_account = SavingsAccount.objects.create(
            account_no='CS987', client=self.member, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=10000,
            annual_interest_rate=1, created_by=self.user, status='Approved')
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 897, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": 3, "total_amount": 1003,
            "totalamount_in_words": '1 rupee', 'client_name': self.member.first_name, 'client_account_number': self.member.account_number,
            'staff_username': self.user.username})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_valid4(self):
        self.group_savings_account = SavingsAccount.objects.create(
            account_no='CS321', group=self.group1, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=10000,
            annual_interest_rate=1, created_by=self.user, status='Approved')
        self.member_savings_account = SavingsAccount.objects.create(
            account_no='CS987', client=self.member, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=10000,
            annual_interest_rate=1, created_by=self.user, status='Approved')
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 897, "payment_type": 'SavingsWithdrawal', "amount": 1000,
            "interest": 3, "total_amount": 1003,
            "totalamount_in_words": '1 rupee', 'group_name': self.group1.name,
            'staff_username': self.user.username, 'group_account_number': self.group1.account_number})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_valid5(self):
        self.grouploan1 = LoanAccount.objects.create(
            account_no='GL98', interest_type='Flat', group=self.group1,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 232, "payment_type": 'Loans', "amount": 12000,
            "total_amount": 12000,
            "totalamount_in_words": '1 rupee', 'group_name': self.group1.name,
            'staff_username': self.user.username, 'group_account_number': self.group1.account_number,
            'group_loan_account_no': self.grouploan1.id})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_valid6(self):
        self.memberloan8 = LoanAccount.objects.create(
            account_no='CL11213', interest_type='Flat', client=self.member,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 232, "payment_type": 'Loans', "amount": 12000,
            "total_amount": 12000,
            "totalamount_in_words": '1 rupee', 'client_name': self.member.first_name,
            'staff_username': self.user.username, 'client_account_number': self.member.account_number,
            'member_loan_account_no': self.memberloan8.id})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_valid7(self):
        self.fixed_deposit52 = FixedDeposits.objects.create(
            client=self.member, deposited_date='2016-8-10', status='Opened',
            fixed_deposit_number='f52', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=1,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 753, "payment_type": 'FixedWithdrawal', "amount": 1200,
            "interest": 1.016393, "total_amount": 1201.016393,
            "totalamount_in_words": '1 rupee', 'client_name': self.member.first_name, 'client_account_number': self.member.account_number,
            'staff_username': self.user.username, 'fixed_deposit_account_no': self.fixed_deposit52.fixed_deposit_number})
        self.assertEqual(response.status_code, 200)

    def test_paymentview_valid8(self):
        self.recurring_deposit1 = RecurringDeposits.objects.create(
            client=self.member, deposited_date='2016-8-10',
            reccuring_deposit_number='r161', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=12,
            recurring_deposit_interest_rate=1, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M', number_of_payments=1,
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        response = self.client.post(reverse("core:payslip"), {
            "date": '10/10/2016', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'RecurringWithdrawal', "amount": 1200,
            "interest": 1.016393, "total_amount": 1201.016393,
            "totalamount_in_words": '1 rupee', 'client_name': self.member.first_name, 'client_account_number': self.member.account_number,
            'staff_username': None, 'recurring_deposit_account_no': self.recurring_deposit1.reccuring_deposit_number})
        self.assertEqual(response.status_code, 200)

    # Receipts Views Tests
    def test_receiptsView1(self):
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '10/10/2014', 'name': self.member.first_name,
             'account_number': "", "branch": self.branch.id,
             "receipt_number": 1})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView2(self):
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 1, "branch": self.branch.id,
             "receipt_number": 1, 'sharecapital_amount': 100, 'entrancefee_amount': 100,
             "membershipfee_amount": 99, "bookfee_amount": 155})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView3(self):
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 1, "branch": self.branch.id,
             "receipt_number": 1, 'loan_account_no': self.memberloan.account_no,
             'loanprocessingfee_amount': 100})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView4(self):
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 1, "branch": self.branch.id,
             "receipt_number": 1, 'savingsdeposit_thrift_amount': 100,
             'loanprocessingfee_amount': ""})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView5(self):
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 1, "branch": self.branch.id,
             "receipt_number": 1, 'savingsdeposit_thrift_amount': "",
             'recurringdeposit_amount': "1200", 'recurring_deposit_account_no': self.recurring_deposit.reccuring_deposit_number})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView6(self):
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 1, "branch": self.branch.id, "fixeddeposit_amount": 1200,
             "receipt_number": 1, 'savingsdeposit_thrift_amount': "",
             'fixed_deposit_account_no': self.fixed_deposit11.fixed_deposit_number})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView7(self):
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 1, "branch": self.branch.id,
             "receipt_number": 1, 'savingsdeposit_thrift_amount': "100",
             "group_name": self.group1.name, "group_account_number": self.group1.account_number
             })
        self.assertEqual(response.status_code, 200)

    # def test_receiptsView8(self):
    #     response = self.client.post(reverse("core:receiptsdeposit"), {
    #          "date": '2014-10-10', 'name': self.member.first_name,
    #          'account_number': 1, "branch": self.branch.id,
    #          "receipt_number": 1, 'insurance_amount': "100"})
    #     self.assertEqual(response.status_code, 200)

    def test_receiptsView9(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000",
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=0, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="12000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 20})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView10(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000",
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=0, principle_repayment=0,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="12000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 20})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView11(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000",
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=0, principle_repayment=0,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="12000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 2})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView12(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000", no_of_repayments_completed=13,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 20})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView13(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Declining',
            status="Approved", loan_amount="12000", no_of_repayments_completed=13,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 20})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView14(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000", no_of_repayments_completed=13,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 2})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView15(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Declining',
            status="Approved", loan_amount="12000", no_of_repayments_completed=13,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 2})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView16(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Declining',
            status="Approved", loan_amount="12000", no_of_repayments_completed=13,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=0,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 2})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView17(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000", no_of_repayments_completed=10,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 20})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView18(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000", no_of_repayments_completed=10,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 2})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView19(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Declining',
            status="Approved", loan_amount="12000", no_of_repayments_completed=10,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "0",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 2})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView20(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000", no_of_repayments_completed=10,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=11000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "1000",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 0})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView21(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000", no_of_repayments_completed=10,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=1000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "1000",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 0})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView22(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount=12000, no_of_repayments_completed=9,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=10000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid=1000)
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "1000",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 0})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView23(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount="12000", no_of_repayments_completed=10,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=100, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid="1000")
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "100",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 0})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView24(self):
        self.member = Client.objects.create(
            first_name="Member0123", last_name="microPyramid", created_by=self.user,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=5123, gender="F",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.group2 = Group.objects.create(
            name='group2', created_by=self.user, account_number='G3w',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.member)
        self.group2.save()

        self.grouploan = LoanAccount.objects.create(
            account_no='GL123', interest_type='Flat', group=self.group2,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=0, total_loan_amount_repaid=12000,
            principle_repayment=1000, loan_issued_by=self.user, loan_issued_date='2016-9-1')
        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount=12000, no_of_repayments_completed=9,
            loan_repayment_period=12, loan_repayment_every=1, loan_repayment_amount=1200,
            annual_interest_rate=2, loan_issued_date='2016-9-1',
            interest_charged=20, total_loan_balance=10000, principle_repayment=1000,
            group_loan_account=self.grouploan, client=self.member, total_loan_amount_repaid=1000)
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 5123, "branch": self.branch.id, 'loanprinciple_amount': "100",
             "receipt_number": 10, "group_name": self.group2.name, 'group_account_number': self.group2.account_number,
             "group_loan_account_no": self.grouploan.account_no, "loaninterest_amount": 0})
        self.assertEqual(response.status_code, 200)

    def test_receiptsView25(self):
        response = self.client.post(reverse("core:receiptsdeposit"), {
             "date": '2014-10-10', 'name': self.member.first_name,
             'account_number': 1, "branch": self.branch.id,
             "receipt_number": 1, "insurance_amount": 100})
        self.assertEqual(response.status_code, 200)

    def test_recurringdepositpaidaccounts(self):
        self.recurring_deposit22 = RecurringDeposits.objects.create(
            client=self.member, deposited_date='2014-1-1',
            reccuring_deposit_number='r221', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        response = self.client.post(reverse("core:getmemberrecurringdepositpaidaccounts"), {
            'recurring_deposit_account_no': self.recurring_deposit22.reccuring_deposit_number,
            "client_name": self.member.first_name, "client_account_number": 1})
        self.assertEqual(response.status_code, 200)

    def test_recurringdepositpaidaccounts1(self):
        self.recurring_deposit22 = RecurringDeposits.objects.create(
            client=self.member, deposited_date='2014-1-1',
            reccuring_deposit_number='r221', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')
        response = self.client.post(reverse("core:getmemberrecurringdepositpaidaccounts"), {
            'recurring_deposit_account_no': self.recurring_deposit22.reccuring_deposit_number
            })
        self.assertEqual(response.status_code, 200)

