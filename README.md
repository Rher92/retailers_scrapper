# retailers_scrapper

### Development & Production Enviroment
the commands below are to start the development enviroment, create admin-user, charge prices, products into database and other things.

If the deployment will be through Docker Compose you can use these commands and instructions too.

```sh
$ docker-compose up --build
$ docker-compose exec web python manage.py createsuperuser
$ docker-compose exec web python manage.py loaddata prices.json
$ docker-compose exec web python manage.py loaddata products.json
```

other commands could be executed from the line command are
```sh
$ docker-compose exec web python manage.py delete_prices_duplicated
$ docker-compose exec web python manage.py delete_products_duplicated
$ docker-compose exec web python manage.py scrape_plaza_vea
$ docker-compose exec web python manage.py scrape_tottus
$ docker-compose exec web python manage.py show_urls
$ docker-compose exec web python manage.py amounts
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

In order to run the retailers in production
```sh
$ docker-compose -f docker-compose.prod.yml up --build
```

how to get API:
| Action | endpoint |
| ------ | ------ |
| get product | /api/products/<sku> |
| get historic prices | /api/products/<sku>/prices |

NOTE: in order for the crawler/scraper/parser to run optimally rhere should be at leats 6 workers running and one crawler/scraper/parser running uniquetly.
