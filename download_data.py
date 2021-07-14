from time import sleep

from random import random

from config import TOKEN
from tinder_api import TinderAPI

if __name__ == "__main__":
    api = TinderAPI(TOKEN)

    new_person_counter = 1
    counter = 1
    while True:
        persons = api.nearby_persons()
        for person in persons:
            print(f'{new_person_counter}/{counter}\t{person.name}...', end=' ')
            if person.download_data(sleep_max_for=random() * 3):
                new_person_counter += 1
            counter += 1
            sleep(random() * 10)
        sleep(random() * 10)
