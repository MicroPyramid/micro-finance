from django.test import TestCase
from micro_admin.forms import *
from micro_admin.models import *
from django.test import Client as TestClient
from tempfile import NamedTemporaryFile
from micro_admin.templatetags import ledgertemplatetags

# Create your tests here.
class Modelform_test(TestCase):
	def setUp(self):
		self.b=Branch.objects.create(name='sbh', opening_date='2014-10-10', country='ind', state='AP', district='Nellore', city='Nellore', area='circle', phone_number=944454651165, pincode=502286)
		self.u = User.objects.create_superuser('jag123','jagadeesh123@gmail.com')
		self.f = NamedTemporaryFile(delete=False, suffix='.jpg',)

	def test_BranchForm(self):
		form = BranchForm(data = {'name':'andhra', 'opening_date':'12/10/2014', 'country':'ind', 'state':'AP', 'district':'Nellore', 'city':'Nellore', 'area':'circle', 'phone_number':944454651165, 'pincode':502286})
		self.assertTrue(form.is_valid())
		branchf=form.save()

	def test_UserForm(self):
		form = UserForm(data={'email':'jag@gmail.com', 'first_name':'jagadeesh', 'gender':'M', 'branch':self.b.id, 'user_roles':'BranchManager', 'username':'jagadeesh', 'password':'jag123'})
		self.assertTrue(form.is_valid())
		userf=form.save()

	def test_GroupForm(self):
		form = GroupForm(data={"name":'Star', "account_number":123456, "activation_date":'10/10/2014', "branch":self.b.id})
		self.assertTrue(form.is_valid())
		groupf=form.save(commit=False)
		groupf.created_by=self.u
		groupf.save()

	def test_ClientForm(self):
		form = ClientForm(data={"first_name":"Micro", "last_name":"Pyramid", "date_of_birth":'10/10/2014', "joined_date":"10/10/2014", "branch":self.b.id, "account_number":123, "gender":"M", "client_role":"FirstLeader", "occupation":"Teacher", "annual_income":2000, "country":'Ind', "state":'AP',"district":'Nellore', "city":'Nellore', "area":'rfc'})
		self.assertTrue(form.is_valid())

	def test_ClientSavingsAccountForm(self):
		form = ClientSavingsAccountForm(data={"account_no":12345, "opening_date":'10/10/2014', "min_required_balance":0, "annual_interest_rate":0})
		self.assertTrue(form.is_valid())

	def test_ClientLoanAccountForm(self):
		form = ClientLoanAccountForm(data={"account_no":12,'created_by':self.u.id, "loan_amount":10000, "interest_type":'Flat', "loan_repayment_period":123, "loan_repayment_every":12, "annual_interest_rate":12, "loanpurpose_description":'Hospitality'})
		self.assertTrue(form.is_valid())

	def test_GroupSavingsAccountForm(self):
		form = GroupSavingsAccountForm(data={"account_no":123, "opening_date":'10/10/2014', "min_required_balance":0, "annual_interest_rate":3})
		self.assertTrue(form.is_valid())

	def test_GroupLoanAccountForm(self):
		form = GroupLoanAccountForm(data={"account_no":123, "interest_type":'Flat', "loan_amount":1000, "loan_repayment_period":10, "loan_repayment_every":10, "annual_interest_rate":3, "loanpurpose_description":'self finance'})
		self.assertTrue(form.is_valid())

	def test_ReceiptForm(self):
		form = ReceiptForm(data={"date":'10/10/2014', "branch":self.b.id, "receipt_number":12345})
		self.assertTrue(form.is_valid())

	def test_PaymentForm(self):
		form = PaymentForm(data={"date":'10/10/2014', "branch":self.b.id, "voucher_number":1231, "payment_type":'Loans', "amount":500, "interest":3, "total_amount":5000, "totalamount_in_words":'1 rupee'})
		self.assertTrue(form.is_valid())

	def test_FixedDepositForm(self):
		form = FixedDepositForm(data={"nominee_firstname":'john', "nominee_lastname":'kumar', "nominee_occupation":'Big data analyst', "fixed_deposit_number":12, "deposited_date":'10/10/2014', "fixed_deposit_amount":12, "fixed_deposit_period":10, "fixed_deposit_interest_rate":3, "relationship_with_nominee":'friend', "nominee_photo":self.f, "nominee_signature":self.f})
		#self.assertTrue(form.is_valid())

	def test_ReccuringDepositForm(self):
		form = ReccuringDepositForm(data={"nominee_firstname":'john', "nominee_lastname":'johny', "nominee_occupation":'devoloper', "reccuring_deposit_number":123, "deposited_date":'10/10/2014', "recurring_deposit_amount":500, "recurring_deposit_period":20, "recurring_deposit_interest_rate":20, "relationship_with_nominee":'friend', "nominee_photo":self.f, "nominee_signature":self.f})
		#self.assertTrue(form.is_valid())



class template_tags(TestCase):

	def test_demand_collections_difference(self):
		res = ledgertemplatetags.demand_collections_difference(20, 10)
		self.assertEqual(res,10)


class Admin_Views_test(TestCase):
	# def setUp(self):
	# 	self.client=TestClient()
	# 	self.user = User.objects.create_superuser('jagadeesh', 'jag123')
	# 	self.b = Branch.objects.create(name='sbh', opening_date='2014-10-10', country='ind', state='AP', district='Nellore', city='Nellore', area='circle', phone_number=944454651165, pincode=502286)
	# 	self.u = User.objects.create_user('jag','jagadeesh@gmail.com')
	# 	self.c = Client.objects.create(first_name="Micro", last_name="Pyramid",created_by=self.u , date_of_birth='2014-10-10', joined_date="2014-10-10", branch = self.b, account_number=123, gender="M", client_role="FirstLeader", occupation="Teacher", annual_income=2000, country='Ind', state='AP',district='Nellore', city='Nellore', area='rfc')
	# 	self.s = SavingsAccount.objects.create(account_no=123456,client=self.c, opening_date='2014-10-10', min_required_balance=0, annual_interest_rate=0)

	def setUp(self):
		self.user = User.objects.create_superuser('jagadeesh', 'jag123')
		self.b = Branch.objects.create(name='sbh', opening_date='2014-10-10', country='ind', state='AP', district='Nellore', city='Nellore', area='circle', phone_number=944454651165, pincode=502286)
		self.u = User.objects.create_user(username='jag',email='jagadeesh@gmail.com',branch=self.b,password='jag')
		self.c = Client.objects.create(first_name="Micro", last_name="Pyramid",created_by=self.u , date_of_birth='2014-10-10', joined_date="2014-10-10", branch = self.b, account_number=123, gender="M", client_role="FirstLeader", occupation="Teacher", annual_income=2000, country='Ind', state='AP',district='Nellore', city='Nellore', area='rfc')
		self.cs = SavingsAccount.objects.create(account_no='CS1',client=self.c, opening_date='2014-1-1', min_required_balance=0, annual_interest_rate=1,created_by=self.u,status='Approved')
		self.g = Group.objects.create(name='group1', created_by=self.u, account_number='G1', activation_date='2014-1-1', branch=self.b)
		self.g.clients.add(self.c)
		self.g.save()
		self.c.status = 'Assigned'
		self.c.save()
		self.gs = SavingsAccount.objects.create(account_no='GS1',group=self.g, opening_date='2014-1-1', min_required_balance=0, annual_interest_rate=1,created_by=self.u,status='Approved')
		grouploan = LoanAccount.objects.create(account_no='GL1', interest_type='Flat', group=self.g, created_by=self.u,status="Approved", loan_amount=12000,          loan_repayment_period=12,loan_repayment_every=1,annual_interest_rate=2, loanpurpose_description='Home Loan',interest_charged=20,total_loan_balance=12000,principle_repayment=1000)
		clientloan = LoanAccount.objects.create(account_no='CL1', interest_type='Flat', client=self.c, created_by=self.u,status="Approved", loan_amount=12000,          loan_repayment_period=12,loan_repayment_every=1,annual_interest_rate=2, loanpurpose_description='Home Loan',interest_charged=20,total_loan_balance=12000,principle_repayment=1000)


	def test_views(self):
		client = Client()
		user_login=self.client.login(username='jagadeesh',password='jag123')
		self.assertTrue(user_login)

		response = self.client.get('/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'login.html')

		response = self.client.get('/createbranch/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'createbranch.html')


		response = self.client.get('/createclient/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'createclient.html')

		response = self.client.get('/createuser/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'createuser.html')

		response = self.client.get('/creategroup/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'creategroup.html')

		response = self.client.get('/editbranch/1/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'editbranchdetails.html')


		response = self.client.get('/edituser/1/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'edituser.html')


		response = self.client.get('/branchprofile/1/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'branchprofile.html')


		response = self.client.get('/userprofile/1/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'userprofile.html')


		response = self.client.get('/userslist/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'listofusers.html')


		response = self.client.get('/viewbranch/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'viewbranch.html')


		response = self.client.get('/groupslist/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'listofgroups.html')


		response = self.client.get('/viewclient/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'viewclient.html')


		response = self.client.get('/deletebranch/1/')
		self.assertEqual(response.status_code,200)


		response = self.client.get('/userchangepassword/1/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'user_change_password.html')


		response = self.client.get('/daybookpdfdownload/2014-10-10/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'pdf_daybook.html')


		response = self.client.get('/generalledgerpdfdownload/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'pdfgeneral_ledger.html')


		response = self.client.get('/paymentslist/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'list_of_payments.html')


		response = self.client.get('/recurringdeposits/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'recurring_deposit_application.html')

	def test_views_post_data(self):
		user_login=self.client.login(username='jag',password='jag')
		self.assertTrue(user_login)

		response = self.client.post('/createbranch/',{'name':'andhra', 'opening_date':'12/10/2014', 'country':'ind', 'state':'AP', 'district':'Nellore', 'city':'Nellore', 'area':'circle', 'phone_number':944454651165, 'pincode':502286})
		self.assertEqual(response.status_code,200)
		self.assertTrue('"error": false' in response.content )

		response = self.client.post('/editbranch/2/',{'name':'andhra', 'opening_date':'12/10/2014', 'country':'ind', 'state':'AP', 'district':'Nellore', 'city':'Nellore', 'area':'circle', 'phone_number':944454651165, 'pincode':502286})
		self.assertEqual(response.status_code,200)
		self.assertTrue('"error": false' in response.content )

		response = self.client.post('/createclient/',{"first_name":"Micro", "last_name":"Pyramid","created_by":self.u.username, "date_of_birth":'10/10/2014', "joined_date":"10/10/2014", "branch":self.b.id, "account_number":561, "gender":"M", "client_role":"FirstLeader", "occupation":"Teacher", "annual_income":2000, "country":'Ind', "state":'AP',"district":'Nellore', "city":'Nellore', "area":'rfc'})
		self.assertTrue('"error": false' in response.content)
		self.assertEqual(response.status_code,200)

		response = self.client.post('/createuser/',{'email':'jag1221@gmail.com', 'first_name':'jag123223', 'gender':'M', 'branch':self.b.id, 'user_roles':'BranchManager', 'username':'jagadeesh121', 'password':'jag123'})
		self.assertTrue('"error": false}' in response.content)
		self.assertEqual(response.status_code,200)

		response = self.client.post('/creategroup/',{"name":'Star', "account_number":123456,"created_by":self.u.username, "activation_date":'10/10/2014', "branch":self.b.id})
		self.assertTrue('"error": false}' in response.content)
		self.assertEqual(response.status_code,200)

		response = self.client.post('/editbranch/1',{'name':'andhra', 'opening_date':'12/10/2014', 'country':'ind', 'state':'AP', 'district':'Nellore', 'city':'Nellore', 'area':'circle', 'phone_number':944454651165, 'pincode':502286})
		self.assertEqual(response.status_code,301)

		response = self.client.post('/edituser/1',{'email':'jag@gmail.com', 'first_name':'jagadeesh', 'gender':'M', 'branch':self.b.id, 'user_roles':'BranchManager', 'username':'jagadeesh', 'password':'jag123'})
		self.assertEqual(response.status_code,301)

		response = self.client.post('/editclient/1/', {"first_name":"Micro", "last_name":"Pyramid", "date_of_birth":'10/10/2014', "joined_date":"10/10/2014", "branch":self.b.id, "account_number":123, "gender":"M", "client_role":"FirstLeader", "occupation":"Teacher", "annual_income":2000, "country":'Ind', "state":'AP',"district":'Nellore', "city":'Nellore', "area":'rfc'})
		self.assertTrue('"error": false}' in response.content)
		self.assertEqual(response.status_code,200)

		response = self.client.post('/groupsavingsapplication/1',{"account_no":123, "opening_date":'10/10/2014', "min_required_balance":0, "annual_interest_rate":3})
		self.assertEqual(response.status_code,301)

		response = self.client.post('/grouploanapplication/1/',{"account_no":123, "interest_type":'Flat', "created_by":self.u.username, "loan_amount":1000, "loan_repayment_period":10, "loan_repayment_every":10, "annual_interest_rate":3, "loanpurpose_description":'self finance'})
		self.assertEqual(response.status_code,200)

		response = self.client.post('/receiptsdeposit/',{"date":'10/10/2014', 'name':self.c.first_name,'account_number':123, "branch":self.b.id, "receipt_number":12345, 'loan_account_no':123,'sharecapital_amount':200, 'savingsdeposit_thrift_amount':200})
		#print response.content
		self.assertEqual(response.status_code,200)

		response = self.client.get('/daybookpdfdownload/2014-10-10')
		print response.content
		self.assertEqual(response.status_code,301)

		response = self.client.post('/clientloanapplication/1',{"account_no":12,'created_by':self.u.id, "created_by":self.u.username, "loan_amount":10000, "interest_type":'Flat', "loan_repayment_period":123, "loan_repayment_every":12, "annual_interest_rate":12, "loanpurpose_description":'Hospitality'})
		self.assertEqual(response.status_code,301)

		# response = self.client.get('/updateclientprofile/1/')
		# self.assertEqual(response.status_code,200)

		response = self.client.get('/clientprofile/1/')
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed('clientprofile.html')

		response = self.client.get('/groupprofile/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/userslist/')
		self.assertEqual(response.status_code,200)

		response = self.client.get('/viewbranch/')
		self.assertEqual(response.status_code,200)

		response = self.client.get('/groupslist/')
		self.assertEqual(response.status_code,200)

		response = self.client.get('/viewclient/')
		self.assertEqual(response.status_code,200)

		response = self.client.get('/assignstaff/1')
		self.assertEqual(response.status_code,301)

		response = self.client.post('/assignstaff/1/',{'staff':1})
		self.assertTrue('"error": false}' in response.content)
		self.assertEqual(response.status_code,200)


		response = self.client.get('/addmember/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/addmember/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/viewmembers/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/groupmeetings/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/addgroupmeeting/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/addgroupmeeting/1',{'meeting_date':'2014/10/10:10-10-10'})
		self.assertEqual(response.status_code,301)

		response = self.client.get('/clientsavingsapplication/1')
		self.assertEqual(response.status_code,301)

		response = self.client.post('/clientsavingsapplication/1',{"account_no":12345, "opening_date":'10/10/2014', "min_required_balance":0, "annual_interest_rate":0, })
		self.assertEqual(response.status_code,301)
		print response.content

		response = self.client.get('/clientsavingsaccount/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/groupsavingsapplication/1')
		self.assertEqual(response.status_code,301)

		response = self.client.post('/groupsavingsapplication/1',{"account_no":123, "opening_date":'10/10/2014','created_by':self.u.id,'status':"Applied", "min_required_balance":0, "annual_interest_rate":3})
		print response.content
		self.assertEqual(response.status_code,301)

		response = self.client.get('/groupsavingsapplication/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/groupsavingsapplication/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/groupsavingsapplication/1',{"account_no":123, "opening_date":'10/10/2014', "min_required_balance":0, "annual_interest_rate":3})
		print response.content
		self.assertEqual(response.status_code,301)

		response = self.client.get('/groupsavingsaccount/1')
		self.assertEqual(response.status_code,301)

		response = self.client.post('/approvesavings/1', {'savingsaccount_id':1})
		self.assertEqual(response.status_code,301)

		response = self.client.get('/rejectsavings/1')
		self.assertEqual(response.status_code,301)

		response = self.client.post('/rejectsavings/1', {'savingsaccount_id':1})
		self.assertEqual(response.status_code,301)


		response = self.client.post('/withdrawsavings/1',{'savingsaccount_id':1})
		self.assertEqual(response.status_code,301)

		response = self.client.get('/viewgroupsavingsdeposits/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/issueloan/1')
		self.assertEqual(response.status_code,301)

		response = self.client.get('/viewgrouptransactions/')
		self.assertEqual(response.status_code,301)
