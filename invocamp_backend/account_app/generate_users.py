import random
import pandas as pd
import re
from faker import Faker
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from account_app.models import Recruiter, Intern, CustomUser,  AccountType

User = get_user_model()
fake = Faker(locale="en_US")

dataset = pd.read_csv(
    '../machine_learning_ops/dataset/dice_com-job_us_sample.csv')

# create a list of unique company names from the dataset
company_names = list(dataset['company'].unique())
# remove duplicates
company_names = list(set(company_names))

addresses = list(dataset['joblocation_address'].unique())

used_company_names = []


def generate_recruiters(num_recruiters=None, loop_all=True):
  if loop_all:
    num_recruiters = len(company_names)

  for i in range(num_recruiters):
    # randomly select a company name that has not been used before
    while True:
      company_name = random.choice(company_names)
      if company_name not in used_company_names:
        used_company_names.append(company_name)
        break

    # randomly select an address based on the current index
    address = addresses[i % len(addresses)]

    # create a user with a generated email address based on the company name
    generated_email = re.sub(r'[^\w\s]', '', company_name).replace(
        ' ', '.').lower() + '@example.com'

    user = User.objects.create_user(
        password='indonesia1234',
        first_name=company_name,
        last_name='',
        email=generated_email,
        account_type=AccountType.RECRUITER,
    )

    # create a recruiter with a random location and description
    recruiter = Recruiter.objects.create(
        user_profile=user,
        company_name=company_name,
        location_name=address,
        description=fake.text(),
    )

    # set the email as primary and verified
    user.emailaddress_set.create(
        email=user.email,
        verified=True,
        primary=True,
    )


def generate_intern():
  generated_first_name = fake.first_name()
  generated_last_name = fake.last_name()
  generated_email = ""

  if generated_first_name and generated_last_name:
    generated_email = f"{generated_first_name.lower()}.{generated_last_name.lower()}@example.com"
  else:
    generated_email = f"{generated_first_name.lower()}@example.com"

  user = User.objects.create_user(
      password='indonesia1234',
      first_name=generated_first_name,
      last_name=generated_last_name,
      email=generated_email,
      account_type=AccountType.INTERN,
  )
  intern = Intern.objects.create(
      user_profile=user,
      phone_number='12345678900',
      education=fake.text(),
      organization_experience=fake.text(),
      work_experience=fake.text(),
      location_name=fake.city(),
      cv='dummy.pdf',
  )

  user.emailaddress_set.create(
      email=user.email,
      verified=True,
      primary=True,
  )


# for i in range(2):
#   generate_intern()

generate_recruiters(loop_all=True)
