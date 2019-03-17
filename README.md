# Long Running Jobs - Backend Challenge @SocialCops

## Task
The `Collect` platform of SocialCops has a variety of long-running tasks which require time and resources on the servers. The task was to design a system such that these long running jobs can be triggered off and not consume the valuable resources. For this, we have to design the REST APIs with the help of which the client now has the capabilities to pause/stop/terminate the long running jobs.

## Tech Stacks Used
1. Flask (Python Web Framework)
2. Celery (Asynchronous task queue)
3. Redis (Message Broker)
4. Docker-Compose (Running Multi-Container Docker applications)

## Approach Summary
1. Generation of Fake CSV data with the help of Faker.

2. Developed RESTful APIs for handling the export and import operations of the CSV files.

3. Integrated celery tasks on the uploading and downloading operations for managing the long running jobs asynchronously.

4. Implemented functionalities for task pausing and stopping (revoke) over the on-going jobs with the help of REST APIs callings.

5. Packed the solution in a docker container for serving the REST APIs over the production environment.

## Issues
The current app fails to execute over the production environment due to some issues, further assisstance and work is required for the deployment of the app using docker images on the kubernetes.

## Process
The RESTful APIs for implementing pause and stop operations over the long running jobs can be tested in both the local environment as well as the production environment. (The production environment is having some issues and is not able to give the required results and is currently under development)
### Execution over Local Environment
* First extract the project source codes and navigate to the folder named
```
cd socialcops/
```

* Activate the virtual environment using the following command
```
source venv/bin/activate
```

* Next we have to set up redis-server on the system, follow the following digitalocean tutorial
```
https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04
```

* Generate the fake csv data file using the following command
```
python data.py
```
The csv file is saved as `data.csv` inside the `files/datasets` folder.

* Now open another terminal and navigate and activate the virtual environment for that also.

* For running the flask app execute the following command
```
flask run
```

* For running the celery workers execute the following command
```
python run.py
```

* Now open another terminal for testing the APIs using `httpie` package. For installation of the package over Debian based systems execute the following command on the terminal
```
sudo apt-get install httpie
```
A simpler web UI can also be navigated at the address providing csv upload and download operations
```
http://localhost:5000/
```
![FireShot Capture 036 - Welcome to SocialCops_ Task Manager - 127 0 0 1](https://user-images.githubusercontent.com/20622980/54474637-386db780-480d-11e9-9e73-b16b7a3d200a.png)

* For checking the currently executing tasks execute the following command
```
http GET http://localhost:5000/tasks/
```
![Screenshot from 2019-03-16 20-07-35](https://user-images.githubusercontent.com/20622980/54476776-3c0e3800-4827-11e9-84ee-512963bc8089.png)

* For testing the csv upload operation send `POST` request with the csv file location according to the following url
```
http -f POST http://localhost:5000/tasks/upload file@/home/vishalpolley/Desktop/socialcops/api/files/datasets/data.csv
```
![Screenshot from 2019-03-16 20-20-30](https://user-images.githubusercontent.com/20622980/54476940-ff434080-4828-11e9-9c22-ed477d4f9183.png)

  The uploaded csv is saved inside files/uploads folder named data.csv

  Status of the currently executing task on the celery worker
  ![Screenshot from 2019-03-16 20-22-19](https://user-images.githubusercontent.com/20622980/54476978-42051880-4829-11e9-83ec-c9449be74f51.png)

* For testing the csv download operation send `GET` request with the `from` and `till` date parameters in `YYYY-MM-DD` format according to the following url
```
http GET http://localhost:5000/tasks/download from=2010-02-15 till=2019-03-15
```
![Screenshot from 2019-03-16 20-39-23](https://user-images.githubusercontent.com/20622980/54477209-b04ada80-482b-11e9-89e8-6127a3b5d06f.png)

  The download csv is saved inside files/downloads folder with the name formatted as <task_id>.csv (e.g 54476940-ff434080-4828-11e9-9c22-ed477d4f9183.csv)

* For checking the status of the currently executing tasks copy the `task_id` from the currently executing task and send the GET request to the particular url
```
http GET http://localhost:5000/tasks/b88a299c-b2cb-45e2-a0db-ed6244edf47d
```
![Screenshot from 2019-03-16 20-13-50](https://user-images.githubusercontent.com/20622980/54476885-20576180-4828-11e9-9682-8bf2f4891e7c.png)

* For performing `pause` operation on the currently executing task send the GET request with the pause parameter to the task url
```
http GET http://localhost:5000/tasks/b88a299c-b2cb-45e2-a0db-ed6244edf47d/pause
```
![Screenshot from 2019-03-16 20-25-18](https://user-images.githubusercontent.com/20622980/54477044-e25b3d00-4829-11e9-8d0f-0372528d95fc.png)

  Status of the paused task on the celery worker
  ![Screenshot from 2019-03-16 20-28-24](https://user-images.githubusercontent.com/20622980/54477065-16366280-482a-11e9-9d4a-4fd5fabb7cdf.png)


* For performing `stop` operation on the currently executing task send the GET request with the stop parameter to the task url
```
http GET http://localhost:5000/tasks/02834f3d-b594-4eb4-9150-2aa069c36986/stop
```
![Screenshot from 2019-03-16 20-32-38](https://user-images.githubusercontent.com/20622980/54477113-aecce280-482a-11e9-9832-24c9b49ea85a.png)

  Status of the stopped task on the celery worker
  ![Screenshot from 2019-03-16 20-34-34](https://user-images.githubusercontent.com/20622980/54477142-f18eba80-482a-11e9-9832-dc84d16df269.png)

## Execution over Production Environment
* For testing the app over the production environment firstly we have to set up the docker environment on our system, follow the following link to get it installed
```
https://docs.docker.com/install/linux/docker-ce/ubuntu/
```

* Next we have to install docker-compose application for executing multiple docker containers
```
https://docs.docker.com/compose/install/
```

* After that extract the project source codes and navigate to the folder named
```
cd socialcops/
```

* For building up the docker image execute the following docker-compose file on the terminal
```
docker-compose build
```

* Next start the docker containers in the deamon mode with the help of following command
```
docker-compose up -d
```

* For stopping the running docker containers, execute the following command
```
docker-compose stop
```
