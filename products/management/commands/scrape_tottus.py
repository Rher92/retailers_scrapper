from django.core.management.base import BaseCommand, CommandError
from utils.tottus import start_tottus

class Command(BaseCommand):
    help = 'Start crawling, scraping and parsing from Tottus Web'

    def handle(self, *args, **options):
        try:
            print('scrape tottus')
            #start_tottus()
        except Exception as e:
            raise CommandError(f'the action couldnt be executed due to: {e}')

        self.stdout.write(self.style.SUCCESS(f'Successfully!'))