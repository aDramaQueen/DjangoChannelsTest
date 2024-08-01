# DjangoChannelsTest

## Usage

Create a "**.env**" file in root directory of this project. Write following inside:

> DEV_WORKING_DIRECTORY=/path/to/my/docker-volumes
> 
> PORT_REDICT=6379

Migrate
```shell
python manage.py migrate
```

Create a superuser
```shell
python manage.py createsuperuser
```

Run the docker composition (which contains 1 image: [**Redict**](https://redict.io/), a drop-in replacement for redis):
```shell
docker compose up
```

After that start this Django project:
```shell
python manage.py runserver
```
