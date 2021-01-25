from django.core.management.base import BaseCommand, CommandError
from utils.plaza_scrapper import start_plazavea

class Command(BaseCommand):
    help = 'Start crawling, scraping and parsing from Plaza Vea Web'

    def handle(self, *args, **options):
        try:
            start_plazavea()
        except Exception as e:
            raise CommandError(f'the action couldnt be executed due to: {e}')

        self.stdout.write(self.style.SUCCESS(f'Successfully!'))