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
            'name': 'client1', 'account_number': 83})
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

        self.grouploan1 = LoanAccount.objects.create(
            account_no='GL2', interest_type='Flat', group=self.group1,
            created_by=self.user, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000, loan_issued_date=None)

        self.group1memberloan = GroupMemberLoanAccount.objects.create(
            account_no='GL1', interest_type='Flat',
            status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2,
            interest_charged=20, total_loan_balance=12000,
            group_loan_account=self.grouploan, client=self.member)
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

    # def test_GetFixedDepositPaidAccountsView(self):
    #     response = self.client.post(
    #         reverse("core:getmemberfixeddepositpaidaccounts"),
    #         {'fixed_deposit_account_no': self.fixed_deposit11.fixed_deposit_number, 'client': self.client})
    #     self.assertEqual(response.status_code, 200)

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
            client=self.member, deposited_date='2016-8-7', status='Opened',
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
            client=self.member, deposited_date='2016-8-7',
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