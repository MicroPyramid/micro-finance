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

    