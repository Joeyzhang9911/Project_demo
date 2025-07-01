# Cloud-Deployed Website: https://comp3900-frontend-843953114718.australia-southeast1.run.app/

# Technologies Used
- **MySQL**: Relational database for structured data storage.
- **Django REST**: Backend framework for handling API requests, authentication, and business logic.
- **React**: Frontend library for building dynamic user interfaces.

# Docker
This project leverages Docker to build and deploy the codebase both locally and for production environments.
Install Docker for [Windows](https://docs.docker.com/desktop/setup/install/windows-install/), [Mac](https://docs.docker.com/desktop/setup/install/mac-install/), and [Linux](https://docs.docker.com/desktop/setup/install/linux/).

# Environment Variables
The [docker-compose](docker-compose.yml) file will retrieve certain environment variables from
a `.env` file if present. Otherwise, it will use some default values that were populated
for development.

If you wish to use this in production, you can set up a `.env` file by duplicating
and renaming our [.env-template](.env-template) file, which has already been populated
with the same development default values mentioned previously.

Note that after the database has been deployed with a password, it will retain
that password after subsequent builds, even if the environment variable changes.

To fix this issue, you may either prune the database volume or manually change its
password.

Refer to the [Querying MySQL Database](#directly-querying-the-mysql-database)
section for more information on changing the password.

# How to Deploy Locally
To deploy, you can run the following command in the project's root directory.
```
docker compose up
```
If you wish to deploy in detached mode (i.e., in server contexts):
```
docker compose up -d
```
You can then access the frontend website on:
```
localhost:3000
```

# How to Deploy on Cloud
Deploying on cloud depends on your own cloud solution. The existing Dockerfiles
are able to be used in cloud deployment. 

For the frontend service, refer to the Prod-Dockerfile for a production-optimised
build.

# Directly Querying the MySQL Database
Enter the following command to connect to the database Docker container:
```
docker exec -it capstone-project-2025-t1-25t1-3900-h12b-banana-db-1 mysql -u root -p
```
The default password is `3900banana`.

To change the password of the database after it has been created, use the following
commands:
```
docker exec -it capstone-project-2025-t1-25t1-3900-h12b-banana-db-1 mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '<YOUR_NEW_PASSWORD>';
FLUSH PRIVILEGES;
quit
```

# Running Django Migrations
All existing models in the Django backend have had migrations created.

If any updates to a model are made, please run the following commands:
```
docker exec -it capstone-project-2025-t1-25t1-3900-h12b-banana-web-1 python manage.py makemigrations <affected-django-app>
docker exec -it capstone-project-2025-t1-25t1-3900-h12b-banana-web-1 python manage.py migrate --fake-initial
```