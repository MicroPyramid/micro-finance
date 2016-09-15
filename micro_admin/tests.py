from django.test import TestCase
from micro_admin.forms import *
from micro_admin.models import *
from tempfile import NamedTemporaryFile
from micro_admin.templatetags import ledgertemplatetags, loans_tags
from django.core.urlresolvers import reverse


class Modelform_test(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(
            name='sbh', opening_date='2014-10-10', country='ind', state='AP',
            district='Nellore', city='Nellore', area='circle', pincode=502286,
            phone_number=944454651165)
        self.user = User.objects.create_superuser(
            'jag123', 'jagadeesh123@gmail.com')
        self.temp_file = NamedTemporaryFile(delete=False, suffix='.jpg',)

    def test_BranchForm(self):
        form = BranchForm(data={
            'name': 'andhra', 'opening_date': '12/10/2014', 'country': 'ind',
            'state': 'AP', 'district': 'Nellore', 'city': 'Nellore',
            'area': 'circle', 'phone_number': 9444546511, 'pincode': 502286})
        self.assertTrue(form.is_valid())

    # BRANCH FORM INVALID
    def test_BranchForm_invalid(self):
        form = BranchForm(data={
            'name': '', 'opening_date': '', 'country': '', 'state': '',
            'district': '', 'city': '', 'area': '', 'phone_number': '',
            'pincode': ''})
        self.assertFalse(form.is_valid())

    def test_UserForm(self):
        form = UserForm(data={
            'email': 'jag@gmail.com', 'first_name': 'jagadeesh', 'gender': 'M',
            'branch': self.branch.id, 'user_roles': 'BranchManager',
            'username': 'jagadeesh', 'password': 'jag123', "country": 'Ind',
            "state": 'AP', "district": 'Nellore', "city": 'Nellore',
            "area": 'rfc', "mobile": 9444546511, "pincode": 502286})
        self.assertTrue(form.is_valid())

    # USER FORM INVALID
    def test_UserForm_invalid(self):
        form = UserForm(data={
            'email': '', 'first_name': '', 'gender': '',
            'branch': self.branch.id, 'user_roles': '', 'username': '',
            'password': '', 'country': '', 'state': '', 'district': '',
            'city': '', 'area': '', 'mobile': '', 'pincode': ''})
        self.assertFalse(form.is_valid())

    def test_GroupForm(self):
        form = GroupForm(data={
            "name": 'Star', "account_number": 123456,
            "activation_date": '10/10/2014', "branch": self.branch.id})
        self.assertTrue(form.is_valid())

    # GROUP FORM INVALID
    def test_GroupForm1(self):
        form = GroupForm(data={
            "name": "", "account_number": "", "activation_date": "",
            "branch": self.branch.id})
        self.assertFalse(form.is_valid())

    def test_ClientForm(self):
        form = ClientForm(data={
            "first_name": "Micro", "last_name": "Pyramid",
            "date_of_birth": '10/10/2014', "joined_date": "10/10/2014",
            "branch": self.branch.id, "account_number": 123, "gender": "M",
            "client_role": "FirstLeader", "occupation": "Teacher",
            "annual_income": 2000, "country": 'Ind', "state": 'AP',
            "district": 'Nellore', "city": 'Nellore', "area": 'rfc',
            "mobile": 9444546511, "pincode": 502286})
        self.assertTrue(form.is_valid())

    # CLIENT FORM INVALID
    def test_ClientForm_invalid(self):
        form = ClientForm(data={
            "first_name": "", "last_name": "", "date_of_birth": '',
            "joined_date": "", "branch": self.branch.id, "account_number": "",
            "gender": "", "client_role": "", "occupation": "",
            "annual_income": '', "country": '', "state": '', "district": '',
            "city": '', "area": '', "mobile": '', "pincode": ''})
        self.assertFalse(form.is_valid())

    def test_SavingsAccountForm(self):
        form = SavingsAccountForm(data={
            "account_no": 12345, "opening_date": '10/10/2014',
            "min_required_balance": 0, "annual_interest_rate": 0})
        self.assertTrue(form.is_valid())

    def test_LoanAccountForm(self):
        form = LoanAccountForm(data={
            "account_no": 12, 'created_by': self.user.id, "loan_amount": 10000,
            "interest_type": 'Flat', "loan_repayment_period": 123,
            "loan_repayment_every": 12, "annual_interest_rate": 12,
            "loanpurpose_description": 'Hospitality'})
        self.assertTrue(form.is_valid())

    # Loan ACCOUNT FORM INVALID
    def test_LoanAccountForm_invalid(self):
        form = LoanAccountForm(data={
            "account_no": '', 'created_by': self.user.id, "loan_amount": '',
            "interest_type": '', "loan_repayment_period": '',
            "loan_repayment_every": '', "annual_interest_rate": '',
            "loanpurpose_description": ''})
        self.assertFalse(form.is_valid())

    def test_SavingsAccountForm1(self):
        form = SavingsAccountForm(data={
            "account_no": 123, "opening_date": '10/10/2014',
            "min_required_balance": 0,
            "annual_interest_rate": 3})
        self.assertTrue(form.is_valid())

    def test_ReceiptForm(self):
        form = ReceiptForm(data={
            "date": '10/10/2014', "branch": self.branch.id,
            "receipt_number": 12345})
        self.assertTrue(form.is_valid())

    def test_PaymentForm(self):
        form = PaymentForm(data={
            "date": '10/10/2014', "branch": self.branch.id,
            "voucher_number": 1231, "payment_type": 'Loans', "amount": 500,
            "interest": 3, "total_amount": 5000,
            "totalamount_in_words": '1 rupee'})
        self.assertTrue(form.is_valid())

    # PAYMENT FORM INVALID
    def test_PaymentForm_invalid(self):
        form = PaymentForm(data={
            "date": "", "branch": "", "voucher_number": "", "payment_type": "",
            "amount": "", "interest": "", "total_amount": "",
            "totalamount_in_words": ""})
        self.assertFalse(form.is_valid())


class template_tags(TestCase):

    def test_demand_collections_difference(self):
        res = ledgertemplatetags.demand_collections_difference(20, 10)
        self.assertEqual(res, 10)


class Admin_Views_test(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('jagadeesh', 'jag123')
        self.branch = Branch.objects.create(
            name='sbh', opening_date='2014-10-10', country='ind', state='AP',
            district='Nellore', city='Nellore', area='circle', pincode=502286,
            phone_number=944454651165)
        self.branch1 = Branch.objects.create(
            name='sbi', opening_date='2014-10-10', country='ind', state='AP',
            district='Nellore', city='Nellore', area='circle', pincode=502286,
            phone_number=944454651165)
        self.branch2 = Branch.objects.create(
            name='andra', opening_date='2014-10-10', country='ind', state='AP',
            district='Nellore', city='Nellore', area='circle', pincode=502286,
            phone_number=944454651165)

        self.staff = User.objects.create_user(
            username='jag', email='jagadeesh@gmail.com', branch=self.branch,
            password='jag')
        self.staff1 = User.objects.create_user(
            username='ravi', email='ravi@gmail.com', branch=self.branch,
            password='ravi')

        self.member1 = Client.objects.create(
            first_name="Micro", last_name="Pyramid", created_by=self.staff,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=123, gender="M",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP', district='Nellore',
            city='Nellore', area='rfc')
        self.member2 = Client.objects.create(
            first_name="Micro1", last_name="Pyramid", created_by=self.staff,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=1234, gender="M",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP',
            district='Nellore', city='Nellore', area='rfc')

        self.member1_savings_account = SavingsAccount.objects.create(
            account_no='CS1', client=self.member1, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=100,
            annual_interest_rate=1, created_by=self.staff, status='Approved')
        self.member2_savings_account = SavingsAccount.objects.create(
            account_no='CS2', client=self.member2, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=100,
            annual_interest_rate=1, created_by=self.staff,
            status='Approved')

        self.group1 = Group.objects.create(
            name='group1', created_by=self.staff, account_number='1',
            activation_date='2014-1-1', branch=self.branch)
        self.group1.clients.add(self.member1)
        self.group1.save()

        self.member1.status = 'Assigned'
        self.member1.save()

        self.group_client = Client.objects.create(
            first_name="Micro2", last_name="Pyramid", created_by=self.staff,
            date_of_birth='2014-10-10', joined_date="2014-10-10",
            branch=self.branch, account_number=1, gender="M",
            client_role="FirstLeader", occupation="Teacher",
            annual_income=2000, country='Ind', state='AP',
            district='Nellore', city='Nellore', area='rfc')
        self.group_client.status = 'Assigned'
        self.group_client.save()

        self.group2 = Group.objects.create(
            name='group2', created_by=self.staff, account_number='2',
            activation_date='2014-1-1', branch=self.branch)
        self.group2.clients.add(self.group_client)
        self.group2.clients.add(self.member2)
        self.group2.save()

        self.group1_savings_account = SavingsAccount.objects.create(
            account_no='GS1', group=self.group1, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=100,
            annual_interest_rate=1, created_by=self.staff1, status='Approved')
        self.group2_savings_account = SavingsAccount.objects.create(
            account_no='GS2', group=self.group2, opening_date='2014-1-1',
            min_required_balance=0, savings_balance=100,
            annual_interest_rate=1, created_by=self.staff, status='Approved')

        self.grouploan = LoanAccount.objects.create(
            account_no='GL1', interest_type='Flat', group=self.group1,
            created_by=self.staff, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000)
        self.clientloan = LoanAccount.objects.create(
            account_no='CL1', interest_type='Flat', client=self.member1,
            created_by=self.staff, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000)

        self.loanaccount_group2 = LoanAccount.objects.create(
            account_no='GL2', interest_type='Flat', group=self.group2,
            created_by=self.staff, status="Approved", loan_amount=12000,
            loan_repayment_period=12, loan_repayment_every=1,
            annual_interest_rate=2, loanpurpose_description='Home Loan',
            interest_charged=20, total_loan_balance=12000,
            principle_repayment=1000)

        self.fixed_deposit = FixedDeposits.objects.create(
            client=self.member1, deposited_date='2014-1-1', status='Opened',
            fixed_deposit_number='f1', fixed_deposit_amount=1200,
            fixed_deposit_period=12, fixed_deposit_interest_rate=3,
            nominee_firstname='r', nominee_lastname='k', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-10-10', nominee_occupation='teacher')
        self.recurring_deposit = RecurringDeposits.objects.create(
            client=self.member1, deposited_date='2014-1-1',
            reccuring_deposit_number='r1', status='Opened',
            recurring_deposit_amount=1200, recurring_deposit_period=200,
            recurring_deposit_interest_rate=3, nominee_firstname='ra',
            nominee_lastname='ku', nominee_gender='M',
            relationship_with_nominee='friend',
            nominee_date_of_birth='2014-1-1', nominee_occupation='Teacher')

        self.temp_file = NamedTemporaryFile(delete=False, suffix='.jpg',)

        self.receipt = Receipts.objects.create(
            receipt_number=1, date="2015-2-20", staff=self.staff,
            branch=self.branch, client=self.member1,
            entrancefee_amount="100")
        self.payments = Payments.objects.create(
            date="2015-2-20", staff=self.staff, branch=self.branch,
            client=self.member1, payment_type="OtherCharges", voucher_number=1,
            amount=100, total_amount=101, interest=1,
            totalamount_in_words="hundred")

    def test_views(self):
        # client = Client()
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

        response = self.client.get(reverse('micro_admin:createbranch'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'branch/create.html')

        response = self.client.get(reverse('micro_admin:createclient'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/create.html')

        response = self.client.get(reverse('micro_admin:createuser'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/create.html')

        response = self.client.get(reverse('micro_admin:creategroup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/create.html')

        response = self.client.get(reverse(
            "micro_admin:editbranch",
            kwargs={"pk": self.branch.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'branch/edit.html')

        response = self.client.get(reverse(
            "micro_admin:edituser",
            kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/edit.html')

        response = self.client.get(reverse(
            "micro_admin:branchprofile",
            kwargs={"pk": self.branch.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'branch/view.html')

        response = self.client.get(reverse(
            "micro_admin:userprofile",
            kwargs={"pk": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')

        response = self.client.get(reverse(
            "micro_admin:userslist"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/list.html')
        response = self.client.get(reverse(
            "micro_admin:viewbranch"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'branch/list.html')

        response = self.client.get(reverse('micro_admin:groupslist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group/list.html')

        response = self.client.get(reverse('micro_admin:viewclient'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/list.html')

        response = self.client.get(reverse(
            "micro_admin:deletebranch",
            kwargs={"pk": self.branch2.id}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('micro_admin:userchangepassword'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_change_password.html')

        response = self.client.get(reverse(
            "micro_admin:daybookpdfdownload",
            kwargs={"date": "2014-10-10"}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pdf_daybook.html')

        response = self.client.get(reverse('micro_admin:generalledgerpdfdownload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pdfgeneral_ledger.html')

        response = self.client.get(reverse('micro_admin:paymentslist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_of_payments.html')

        response = self.client.get(reverse('micro_admin:recurringdeposits'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'client/recurring-deposits/application.html')

        # with open('static/images/test.png', 'r') as signature:
        #     with open('static/images/test.png', 'r') as photo:
        #         response = self.client.post('/recurringdeposits/', {"nominee_date_of_birth": "2/2/2010", "nominee_gender": "F", "client_name": "Micro", "client_account_no": 123, "nominee_firstname": 'john', "nominee_lastname": 'johny', "nominee_occupation": 'devoloper', "reccuring_deposit_number": 12344, "deposited_date": '10/10/2014', "recurring_deposit_amount": 500, "recurring_deposit_period": 20, "recurring_deposit_interest_rate": 20, "relationship_with_nominee": 'friend', "nominee_signature": signature, "nominee_photo": photo, "client": str(self.member1.id)}, format='multipart/form-data')
        #         self.assertEqual(response.status_code, 200)

        #         response = self.client.post('/recurringdeposits/', {"nominee_date_of_birth": "2/2/2010", "nominee_gender": "F", "client_name": "Micro111", "client_account_no": 123, "nominee_firstname": 'john', "nominee_lastname": 'johny', "nominee_occupation": 'devoloper', "reccuring_deposit_number": 12344, "deposited_date": '10/10/2014', "recurring_deposit_amount": 500, "recurring_deposit_period": 20, "recurring_deposit_interest_rate": 20, "relationship_with_nominee": 'friend', "nominee_signature": signature, "nominee_photo": photo, "client": str(self.member1.id)}, format='multipart/form-data')
        #         self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('micro_admin:recurringdeposits'), {
            "client_name": "Micro", "client_account_no": 123,
            "nominee_date_of_birth": "", "nominee_gender": "",
            "nominee_firstname": '', "nominee_lastname": '',
            "nominee_occupation": '', "reccuring_deposit_number": "",
            "deposited_date": '', "recurring_deposit_amount": "",
            "recurring_deposit_period": "",
            "recurring_deposit_interest_rate": "",
            "relationship_with_nominee": '',
            "nominee_signature": "", "nominee_photo": "",
            "client": self.member1})
        self.assertEqual(response.status_code, 200)

        # with open('static/images/test.png', 'r') as signature:
        #     with open('static/images/test.png', 'r') as photo:
        #         response = self.client.post('/fixeddeposits/', {"client_name": "Micro", "client_account_no": 123, "nominee_firstname": 'john', "nominee_lastname": 'kumar', "nominee_gender": "F", "nominee_date_of_birth": "1/2/2015", "nominee_occupation": 'Big data analyst', "fixed_deposit_number": 12, "deposited_date": '10/10/2014', "fixed_deposit_amount": 12, "fixed_deposit_period": 10, "fixed_deposit_interest_rate": 3, "relationship_with_nominee": 'friend', "nominee_photo": photo, "nominee_signature": signature})
        #         self.assertEqual(response.status_code, 200)

        #         response = self.client.post('/fixeddeposits/', {"client_name": "Micro44", "client_account_no": 123, "nominee_firstname": 'john', "nominee_lastname": 'kumar', "nominee_gender": "F", "nominee_date_of_birth": "1/2/2015", "nominee_occupation": 'Big data analyst', "fixed_deposit_number": 12, "deposited_date": '10/10/2014', "fixed_deposit_amount": 12, "fixed_deposit_period": 10, "fixed_deposit_interest_rate": 3, "relationship_with_nominee": 'friend', "nominee_photo": photo, "nominee_signature": signature})
        #         self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('micro_admin:fixeddeposits'), {
            "client_name": "Micro", "client_account_no": 123,
            "nominee_firstname": '', "nominee_lastname": '',
            "nominee_gender": "", "nominee_date_of_birth": "",
            "nominee_occupation": '', "fixed_deposit_number": "",
            "deposited_date": '', "fixed_deposit_amount": "",
            "fixed_deposit_period": "", "fixed_deposit_interest_rate": "",
            "relationship_with_nominee": '', "nominee_photo": "",
            "nominee_signature": ""})
        self.assertEqual(response.status_code, 200)

        # with open('static/images/test.png', 'r') as signature:
        #     with open('static/images/test.png', 'r') as photo:
        #         response = self.client.post('/client/profile/update/'+str(self.member1.id)+'/', {"photo": photo, "signature": signature})
        #         self.assertEqual(response.status_code, 302)
                # self.assertRedirects(response, '/clientprofile/'+str(self.member1.id)+'/', status_code=302, target_status_code=200)

    def test_views_post_data(self):
        user_login = self.client.login(username='jag', password='jag')
        self.assertTrue(user_login)

        response = self.client.post(reverse("micro_admin:createbranch"), {
            'name': 'andhra', 'opening_date': '12/10/2014', 'country': 'ind',
            'state': 'AP', 'district': 'Nellore', 'city': 'Nellore',
            'area': 'circle', 'phone_number': 944454651165, 'pincode': 502286})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse(
            "micro_admin:editbranch",
            kwargs={"pk": self.branch1.id}),
            {'name': 'andhra', 'opening_date': '12/10/2014', 'country': 'ind',
             'state': 'AP', 'district': 'Nellore', 'city': 'Nellore',
             'area': 'circle', 'phone_number': 944454651165,
             'pincode': 502286})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('micro_admin:createclient'), {
            "first_name": "Micro", "last_name": "Pyramid",
            "created_by": self.staff.username, "date_of_birth": '10/10/2014',
            "joined_date": "10/10/2014", "branch": self.branch.id,
            "account_number": 561, "gender": "M", "client_role": "FirstLeader",
            "occupation": "Teacher", "annual_income": 2000, "country": 'Ind',
            "state": 'AP', "district": 'Nellore', "city": 'Nellore',
            "area": 'rfc', "mobile": 944454651165, "pincode": 502286})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("micro_admin:createuser"), {
            'email': 'jag1221@gmail.com', 'first_name': 'jag123223',
            'gender': 'M', 'branch': self.branch.id,
            'user_roles': 'BranchManager', 'username': 'jagadeesh121',
            'password': 'jag123'})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('micro_admin:creategroup'), {
            "name": 'Star', "account_number": 123456,
            "created_by": self.staff.username,
            "activation_date": '10/10/2014', "branch": self.branch.id})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse(
            "micro_admin:editbranch",
            kwargs={"pk": self.branch1.id}),
            {'name': 'andhra', 'opening_date': '12/10/2014', 'country': 'ind',
             'state': 'AP', 'district': 'Nellore', 'city': 'Nellore',
             'area': 'circle', 'phone_number': 944454651165,
             'pincode': 502286})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse(
            "micro_admin:editbranch",
            kwargs={"pk": self.branch.id}), {
            'email': 'jag@gmail.com', 'first_name': 'jagadeesh',
            'gender': 'M', 'branch': self.branch.id,
            'user_roles': 'BranchManager',
            'username': 'jagadeesh', 'password': 'jag123'})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse(
            "micro_admin:editclient",
            kwargs={"pk": self.member1.id}),
            {"first_name": "Micro", "last_name": "Pyramid",
             "date_of_birth": '10/10/2014', "joined_date": "10/10/2014",
             "branch": self.branch.id, "account_number": 123,
             "gender": "M", "client_role": "FirstLeader",
             "occupation": "Teacher", "annual_income": 2000, "country": 'Ind',
             "state": 'AP', "district": 'Nellore', "city": 'Nellore',
             "area": 'rfc', "mobile": 944454651165, "pincode": 502286})
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse(
            "loans:grouploanapplication",
            kwargs={"group_id": self.group1.id}),
            {"account_no": 123, "interest_type": 'Flat',
             "created_by": self.staff.username, "loan_amount": 1000,
             "loan_repayment_period": 10, "loan_repayment_every": 10,
             "annual_interest_rate": 3,
             "loanpurpose_description": 'self finance'})
        self.assertEqual(response.status_code, 200)

        # response = self.client.post(
        #     reverse("core:receiptsdeposit"),
        #     {"date": '10/10/2014', 'name': self.user.first_name,
        #      'account_number': 123, "branch": self.branch.id,
        #      "receipt_number": 12345, 'loan_account_no': 123,
        #      'sharecapital_amount': 200, 'savingsdeposit_thrift_amount': 200})
        # self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "micro_admin:daybookpdfdownload",
            kwargs={"date": "2014-10-10"}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse(
            'loans:clientloanapplication',
            kwargs={'client_id': self.member1.id}),
            {"account_no": 12, "created_by": self.staff.username,
             "loan_amount": 10000, "interest_type": 'Flat',
             "loan_repayment_period": 123, "loan_repayment_every": 12,
             "annual_interest_rate": 12,
             "loanpurpose_description": 'Hospitality'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "micro_admin:clientprofile",
            kwargs={'pk': self.member1.id}))
        self.assertEqual(response.status_code, 200)

        # response = self.client.get(reverse(
        #     "micro_admin:updateclientprofile",
        #     kwargs={'pk': self.member1.id}))
        # self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed('client/update-profile.html')

        response = self.client.get(
            reverse(
                'micro_admin:groupprofile',
                kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("micro_admin:userslist"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("micro_admin:viewbranch"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('micro_admin:groupslist'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("micro_admin:viewclient"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('micro_admin:assignstaff',
                    kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('micro_admin:assignstaff',
                    kwargs={'group_id': self.group1.id}),
            {'staff': str(self.staff.id)}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('micro_admin:addmember',
                    kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('micro_admin:viewmembers',
                    kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('micro_admin:groupmeetings',
                    kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('micro_admin:addgroupmeeting',
                    kwargs={'group_id': self.group1.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('micro_admin:addgroupmeeting',
                    kwargs={'group_id': self.group1.id}),
            {'meeting_date': '2014/10/10:10-10-10'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('savings:clientsavingsapplication',
                    kwargs={'client_id': self.member1.id}))
        self.assertEqual(response.status_code, 302)

        SavingsAccount.objects.filter(client=self.member1).delete()
        response = self.client.post(
            reverse('savings:clientsavingsapplication',
                    kwargs={'client_id': self.member1.id}),
            {"account_no": 12345, "created_by": self.user.username,
             "opening_date": '10/10/2014', "min_required_balance": 0,
             "annual_interest_rate": 0})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("savings:clientsavingsaccount",
                    kwargs={'client_id': self.member2.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('savings:groupsavingsapplication',
                    kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 302)

        SavingsAccount.objects.filter(group=self.group1).delete()
        response = self.client.post(
            reverse('savings:groupsavingsapplication',
                    kwargs={'group_id': self.group1.id}),
            {"account_no": 123, "created_by": self.user.username,
             "opening_date": '10/10/2014', 'created_by': self.user.id,
             "status": "Applied", "min_required_balance": '',
             "annual_interest_rate": 3}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('savings:groupsavingsapplication',
                    kwargs={'group_id': self.group1.id}),
            {"account_no": 123, "opening_date": '10/10/2014',
             "created_by": self.user.username, "min_required_balance": 0,
             "annual_interest_rate": 3}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("savings:groupsavingsaccount",
                    kwargs={'group_id': self.group2.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("savings:viewgroupsavingsdeposits",
                                           kwargs={'group_id': self.group2.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:issueloan",
                    kwargs={'loanaccount_id': self.loanaccount_group2.id}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("savings:viewgroupsavingswithdrawals",
                                           kwargs={'group_id': self.group2.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse(
            "loans:grouploanapplication",
            kwargs={"group_id": self.group2.id}),
            {"account_no": 1239, "interest_type": 'Flat', "loan_amount": 1000,
             "loan_repayment_period": 10, "loan_repayment_every": 10,
             "annual_interest_rate": 3,
             "loanpurpose_description": 'self finance'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:grouploanaccount",
                    kwargs={'pk': self.grouploan.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("loans:clientloanaccount",
                                           kwargs={'pk': self.clientloan.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:listofclientloandeposits", kwargs={
                'client_id': self.member1.id, 'loanaccount_id': self.clientloan.id})
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("savings:listofclientsavingsdeposits",
                    kwargs={'client_id': self.member2.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:viewgrouploandeposits", kwargs={
                'group_id': self.group1.id, 'loanaccount_id': self.grouploan.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:issueloan",
                    kwargs={'loanaccount_id': self.clientloan.id}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("micro_admin:receiptslist"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:clientloanledgeraccount", kwargs={
                'client_id': self.member1.id, 'loanaccount_id': self.clientloan.id}
            )
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("micro_admin:generalledger"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("micro_admin:fixeddeposits"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "micro_admin:clientfixeddepositsprofile", kwargs={
                'fixed_deposit_id': self.fixed_deposit.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "micro_admin:viewclientfixeddeposits"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("micro_admin:viewdaybook"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse(
            "micro_admin:viewdaybook"), {'date': '10/10/2014'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "micro_admin:viewparticularclientfixeddeposits", kwargs={
                'client_id': self.member1.id}))
        self.assertEqual(response.status_code, 200)

        # response = self.client.get(reverse('core:payslip'))
        # self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "loans:grouploanaccountslist",
            kwargs={'group_id': self.group1.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "loans:clientloanaccountslist",
            kwargs={'client_id': self.member1.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('micro_admin:paymentslist'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "micro_admin:clientrecurringdepositsprofile", kwargs={
                'recurring_deposit_id': self.recurring_deposit.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            'micro_admin:viewclientrecurringdeposits'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "micro_admin:viewparticularclientrecurringdeposits",
            kwargs={'client_id': self.member1.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:clientledgercsvdownload", kwargs={
                'client_id': self.member1.id, 'loanaccount_id': self.clientloan.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:clientledgerexceldownload", kwargs={
                'client_id': self.member1.id, 'loanaccount_id': self.clientloan.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("loans:clientledgerpdfdownload", kwargs={
                'client_id': self.member1.id, 'loanaccount_id': self.clientloan.id})
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            "micro_admin:daybookpdfdownload",
            kwargs={"date": "2014-10-10"}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('micro_admin:generalledgerpdfdownload'))
        self.assertEqual(response.status_code, 200)

        # response = self.client.get('/userchangepassword/1/')
        # self.assertEqual(response.status_code, 200)

    #     response = self.client.post('/userchangepassword/1/', {'current_password': 'jag123', 'new_password': '123123', 'confirm_new_password': '123123'})
    #     self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(reverse('micro_admin:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('micro_admin:login'),
                             status_code=302, target_status_code=200)

    def test_user_logout_without_login(self):
        response = self.client.get(reverse('micro_admin:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response, '')

    def test_user_login_view(self):
        response = self.client.post(reverse('micro_admin:login'), {
            'username': 'jagadeesh', 'password': 'jag123'})
        self.assertEqual(response.status_code, 200)

    def test_user_login_wrong_input(self):
        response = self.client.post(reverse('micro_admin:login'), {
            'username': 'jagadeesh', 'password': ''})
        self.assertEqual(response.status_code, 200)

    def test_create_branch_invalid_post_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(reverse("micro_admin:createbranch"), {
            'name': '', 'opening_date': '', 'country': '', 'state': '',
            'district': '', 'city': '', 'area': '', 'phone_number': '',
            'pincode': ''})
        self.assertEqual(response.status_code, 200)

    def test_create_client_invalid_post_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(reverse("micro_admin:createclient"), {
            "first_name": "", "last_name": "", "date_of_birth": '',
            "joined_date": "", "branch": "", "account_number": "",
            "gender": "", "client_role": "", "occupation": "",
            "annual_income": '', "country": '', "state": '', "district": '',
            "city": '', "area": '', "mobile": '', "pincode": ''})
        self.assertEqual(response.status_code, 200)

    def test_removemembers_from_group_view(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(
            reverse('micro_admin:removemember',
                    kwargs={'group_id': self.group1.id,
                            'client_id': self.member1.id})
        )
        self.assertEqual(response.status_code, 404)

    # def test_create_client_invalid_post_data(self):
    #     user_login = self.client.login(username='jagadeesh', password='jag123')
    #     response = self.client.post('/createuser/', {'email': '', 'first_name': '', 'gender': '', 'branch': self.branch.id, 'user_roles': '', 'username': '', 'password': ''})
    #     self.assertEqual(response.status_code, 200)

    def test_create_group_invalid_post_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(reverse('micro_admin:creategroup'), {
            "name": '', "account_number": '', "activation_date": '',
            "branch": self.branch.id})
        self.assertEqual(response.status_code, 200)

    def test_addmembers_to_group_post_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(
            reverse('micro_admin:addmember',
                    kwargs={'group_id': self.group1.id}),
            {"clients": [self.member1.id]}
        )
        self.assertEqual(response.status_code, 200)

    def test_addmembers_to_group_post_invalid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(
            reverse('micro_admin:addmember',
                    kwargs={'group_id': self.group1.id}),
            {"clients": ""}
        )
        self.assertEqual(response.status_code, 200)

    # def test_group_delete(self):
    #     group_count = Group.objects.count()
    #     response = self.client.get(
    #         reverse('micro_admin:deletegroup',
    #                 kwargs={'group_id': self.group1.id})
    #     )
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(Group.objects.count(), group_count-1)
    #     self.assertRedirects(
    #         response, reverse('micro_admin:groupslist'),
    #         status_code=302, target_status_code=200)

    def test_add_group_meeting_post_invalid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(
            reverse('micro_admin:addgroupmeeting',
                    kwargs={'group_id': self.group1.id}),
            {
                "meeting_date": "",
                "meeting_time": "10-10-10",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str(
            '"meeting_date": ["This field is required."]'
        ) in str(response.content.decode('utf8')))

    def test_add_group_meeting_post_valid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(
            reverse('micro_admin:addgroupmeeting',
                    kwargs={'group_id': self.group1.id}),
            {
                "meeting_date": "2/20/2015",
                "meeting_time": "10-10-10",
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_client_savings_application_post_invalid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(
            reverse('savings:clientsavingsapplication',
                    kwargs={'client_id': self.member1.id}),
            {"account_no": '',
             "opening_date": '',
             "min_required_balance": '',
             "annual_interest_rate": ''}
        )
        self.assertEqual(response.status_code, 302)

    def test_client_savings_application_post_valid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(
            reverse('savings:clientsavingsapplication',
                    kwargs={'client_id': self.member1.id}),
            {"account_no": 123,
             "opening_date": '10/10/2014',
             "min_required_balance": 0,
             "annual_interest_rate": 3}
        )
        self.assertEqual(response.status_code, 302)

    def test_group_savings_application_post_invalid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        SavingsAccount.objects.filter(group=self.group1).delete()
        response = self.client.post(
            reverse('savings:groupsavingsapplication',
                    kwargs={'group_id': self.group1.id}),
            {"account_no": '', "opening_date": '', "min_required_balance": '',
             "annual_interest_rate": ''}
        )
        self.assertEqual(response.status_code, 200)

    def test_group_savings_application_post_valid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(
            reverse('savings:groupsavingsapplication',
                    kwargs={'group_id': self.group1.id}),
            {"account_no": 123, "opening_date": '10/10/2014',
             "min_required_balance": 0, "annual_interest_rate": 3}
        )
        self.assertEqual(response.status_code, 302)

    def test_group_savings_account(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(
            reverse("savings:groupsavingsaccount",
                    kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "group/savings/account.html")

    def test_group_loan_application(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(reverse(
            "loans:grouploanapplication",
            kwargs={"group_id": self.group1.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "group/loan/application.html")

    def test_group_loan_application_post_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(reverse(
            "loans:grouploanapplication",
            kwargs={"group_id": self.group1.id}),
            {"account_no": 12,
             'created_by': self.staff.id,
             "loan_amount": 10000,
             "interest_type": 'Flat',
             "loan_repayment_period": 123,
             "loan_repayment_every": 12,
             "annual_interest_rate": 12,
             "loanpurpose_description": 'Hospitality'})
        self.assertEqual(response.status_code, 200)

    def test_group_loan_application_post_invalid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(reverse(
            "loans:grouploanapplication",
            kwargs={"group_id": self.group1.id}),
            {"account_no": '',
             'created_by': self.staff.id,
             "loan_amount": '',
             "interest_type": '',
             "loan_repayment_period": '',
             "loan_repayment_every": '',
             "annual_interest_rate": '',
             "loanpurpose_description": ''})
        self.assertEqual(response.status_code, 200)

    def test_client_loan_application(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(reverse(
            'loans:clientloanapplication',
            kwargs={'client_id': self.member1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/loan/application.html")

    def test_client_loan_application_post_invalid_data(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(reverse(
            'loans:clientloanapplication',
            kwargs={'client_id': self.member1.id}),
            {"account_no": '',
             'created_by': self.staff.id,
             "loan_amount": '',
             "interest_type": '',
             "loan_repayment_period": '',
             "loan_repayment_every": '',
             "annual_interest_rate": '',
             "loanpurpose_description": ''})
        self.assertEqual(response.status_code, 200)

    def test_listofclient_savings_withdrawals(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(reverse("savings:listofclientsavingswithdrawals",
                                           kwargs={'client_id': self.member1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "client/savings/list_of_savings_withdrawals.html")

    def test_issue_loan_client(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(
            reverse("loans:issueloan",
                    kwargs={'loanaccount_id': self.clientloan.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("loans:clientloanaccount", kwargs={'pk': self.clientloan.id}),
                             status_code=302, target_status_code=200)


    def test_ledger_account(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(
            reverse("loans:clientloanledgeraccount", kwargs={
                'client_id': self.member1.id, 'loanaccount_id': self.clientloan.id}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/loan/client_ledger_account.html")

    def test_general_ledger(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(reverse(
            "micro_admin:generalledger"), {"date": '2015-2-20'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "generalledger.html")

    def test_day_book(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.post(reverse(
            "micro_admin:viewdaybook"), {"date": '2/20/2015'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "day_book.html")

    def test_group_delete(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        response = self.client.get(
            reverse('micro_admin:deletegroup',
                    kwargs={'group_id': self.group1.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('micro_admin:groupslist'),
            status_code=302, target_status_code=200)

    def test_group_delete1(self):
        user_login = self.client.login(username='jagadeesh', password='jag123')
        self.assertTrue(user_login)
        self.group_delete = Group.objects.create(
            name='group10', created_by=self.staff, account_number='10',
            activation_date='2014-1-1', branch=self.branch)
        response = self.client.get(
            reverse('micro_admin:deletegroup',
                    kwargs={'group_id': self.group_delete.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('micro_admin:groupslist'),
            status_code=302, target_status_code=200)
