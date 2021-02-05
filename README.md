# retailers_scrapper

### Development Enviroment
the commands below are to start the development enviroment, create admin-user, charge prices, products into database and other things.

If the deployment will be through Docker Compose you can use these commands and instructions too.

```sh
$ docker-compose up --build
$ docker-compose exec django python manage.py createsuperuser
$ docker-compose exec django python manage.py loaddata prices.json
$ docker-compose exec django python manage.py loaddata products.json
```

other commands could be executed from the line command are
```sh
$ docker-compose exec django python manage.py delete_prices_duplicated
$ docker-compose exec django python manage.py delete_products_duplicated
$ docker-compose exec django python manage.py scrape_plaza_vea
$ docker-compose exec django python manage.py scrape_tottus
$ docker-compose exec django python manage.py show_urls
$ docker-compose exec django python manage.py amounts
```

In order to see how to work Celery through Celery FLower in real-time go to:
http://127.0.0.1:5555/


In order to purge Redis run:
```sh
$ docker-compose exec redis redis-cli
$ FLUSHALL
```

In order to scale up/down some services run:
```sh
$ docker-compose up --scale <service>=<number of services>
e.g.,
$ docker-compose up --scale celery_worker=6 -d
```

how to get API:
| Action | endpoint |
| ------ | ------ |
| get product | /api/products/<sku> |
| get historic prices | /api/products/<sku>/prices |

NOTE: in order for the crawler/scraper/parser to run optimally rhere should be at leats 6 workers running and one crawler/scraper/parser running uniquetly.


### Deployment Enviroment

In order to run the retailers in production
```sh
$ docker-compose -f docker-compose.prod.yml up --build
```

All command above works to Deployemnt enviroment only with an exception:

those will be run as following way:
```sh
$ docker-compose -f docker-compose.prod.yml run --rm ...
```

### Manually changes
- The traefik.yml must be changed according the specifications.

- In order to schedule the execution of the Crawler/Scraper/Parser should be changed CELERY_BEAT_SCHEDULE into settings.py. 

- other differents ways to execute:
    - is through of django admin going into Periodics tasks(previuosly created) take it and run the Run selected task
    - run the command python manage.py scrape_plaza_vea (instructions above)

- Create into the retailers_scrapper root the file .env and copy .envs/.dev-sample and paste into it.
    - those follows vars must be changed:
        - DJANGO_ALLOWED_HOSTS
        - DJANGO_SETTINGS_MODULE
        - POSTGRES_HOST
        - POSTGRES_PORT
        - POSTGRES_DB
        - POSTGRES_USER
        - POSTGRES_PASSWORD
        - DJANGO_DEBUG