from django.test import TestCase
from micro_admin.forms import *
from micro_admin.models import *
from django.test import Client as TestClient

# Create your tests here.
class Modelform_test(TestCase):
	def setUp(self):
		self.b=Branch.objects.create(name='sbh', opening_date='2014-10-10', country='ind', state='AP', district='Nellore', city='Nellore', area='circle', phone_number=944454651165, pincode=502286)

	def test_BranchForm(self):
		form = BranchForm(data = {'name':'andhra', 'opening_date':'12/10/2014', 'country':'ind', 'state':'AP', 'district':'Nellore', 'city':'Nellore', 'area':'circle', 'phone_number':944454651165, 'pincode':502286})
		self.assertTrue(form.is_valid())

	def test_UserForm(self):
		form = UserForm(data={'email':'jag@gmail.com', 'first_name':'jagadeesh', 'gender':'M', 'branch':self.b.id, 'user_roles':'BranchManager', 'username':'jagadeesh', 'password':'jag123'})
		self.assertTrue(form.is_valid())

	def test_GroupForm(self):
		form = GroupForm(data={"name":'Star', "account_number":123456, "activation_date":'10/10/2014', "branch":self.b.id})
		self.assertTrue(form.is_valid())

	def test_ClientForm(self):
		form = ClientForm(data={"first_name":"Micro", "last_name":"Pyramid", "date_of_birth":'10/10/2014', "joined_date":"10/10/2014", "branch":self.b.id, "account_number":123, "gender":"M", "client_role":"FirstLeader", "occupation":"Teacher", "annual_income":2000, "country":'Ind', "state":'AP',"district":'Nellore', "city":'Nellore', "area":'rfc'})
		self.assertTrue(form.is_valid())


class Admin_Views_test(TestCase):
	def setUp(self):
		self.client=TestClient()
		self.user = User.objects.create_superuser('jagadeesh', 'jag123')
		b = Branch.objects.create(name='sbh', opening_date='2014-10-10', country='ind', state='AP', district='Nellore', city='Nellore', area='circle', phone_number=944454651165, pincode=502286)
		u = User.objects.create_user('jag','jagadeesh@gmail.com')
		u.branch = b
		u.save()
		c = Client.objects.create(first_name="Micro", last_name="Pyramid",created_by=u , date_of_birth='2014-10-10', joined_date="2014-10-10", branch = b, account_number=123, gender="M", client_role="FirstLeader", occupation="Teacher", annual_income=2000, country='Ind', state='AP',district='Nellore', city='Nellore', area='rfc')

	def test_views(self):
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


		response = self.client.get('/branchprofile/1')
		self.assertEqual(response.status_code,301)
		#self.assertTemplateUsed(response,'branchprofile.html')


		response = self.client.get('/userprofile/1')
		self.assertEqual(response.status_code,301)
		#self.assertTemplateUsed(response,'userprofile.html')


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

		# response = self.client.get('/updateclientprofile/1/')
		# self.assertEqual(response.status_code,200)

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
		user_login=self.client.login(username='jagadeesh',password='jag123')
		self.assertTrue(user_login)

		response = self.client.post('/createbranch/',{'name':'andhra', 'opening_date':'12/10/2014', 'country':'ind', 'state':'AP', 'district':'Nellore', 'city':'Nellore', 'area':'circle', 'phone_number':944454651165, 'pincode':502286})
		self.assertEqual(response.status_code,200)
		self.assertTrue('"error": false' in response.content )

		response = self.client.post('/editbranch/2/',{'name':'andhra', 'opening_date':'12/10/2014', 'country':'ind', 'state':'AP', 'district':'Nellore', 'city':'Nellore', 'area':'circle', 'phone_number':944454651165, 'pincode':502286})
		self.assertEqual(response.status_code,200)
		self.assertTrue('"error": false' in response.content )
