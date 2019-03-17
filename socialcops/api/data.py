import csv
from time import time
from faker import Faker

fake = Faker('en_GB')
RECORD_COUNT = 100000

# Function for generating fake data and saving them to csv file
def create_csv_file():
    with open('./files/datasets/data.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'age', 'phone', 'email', 'address',
                      'record_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(RECORD_COUNT):
            writer.writerow(
                {
                    'name': fake.name(),
                    'age': fake.random_int(min=1, max=80),
                    'phone': fake.phone_number(),
                    'email': fake.email(),
                    'address': fake.street_address(),
                    'record_date': fake.date_this_decade(before_today=True, after_today=False),
                }
            )

if __name__ == '__main__':
    start = time()
    create_csv_file()
    elapsed = time() - start
    print('created csv file time: {}'.format(elapsed))
