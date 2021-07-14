from time import time, sleep
from random import random
import csv

import tensorflow.compat.v1 as tf

from config import TOKEN, PROF_DATA
from tinder_api import TinderAPI
from likeliness_classifier import Classifier
import person_detector

if __name__ == "__main__":
    api = TinderAPI(TOKEN)
    likes_real = {}
    with open(PROF_DATA, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                likes_real[row['id']] = float(row['like'])
            except:
                pass

    detection_graph = person_detector.open_graph()
    with detection_graph.as_default():
        with tf.Session() as sess:

            classifier = Classifier(graph="./tf/training_output/retrained_graph.pb",
                                    labels="./tf/training_output/retrained_labels.txt")

            end_time = time() + 60 * 60 * 2
            while time() < end_time:
                print(f"------\tTIME LEFT: {(end_time - time()) / 60} min\t-----")
                persons = api.nearby_persons()
                pos_schools = ['ниу вшэ', 'высшая школа экономики']

                for person in persons:
                    try:
                        print("-------------------------")
                        print("ID: ", person.id)
                        print("Name: ", person.name)
                        print("Schools: ", person.schools)
                        print("Images:")
                        [print(f'{i + 1}\t{image}') for i, image in enumerate(person.images)]

                        if person.id in likes_real:
                            score = likes_real[person.id]
                            sleep(random() * 3)
                        else:
                            score = person.predict_likeliness(classifier, sess)

                        for school in person.schools:
                            if school.lower() in pos_schools:
                                print('School match')
                                score *= 1.2
                                break

                        print("SCORE: ", score)
                        if score > 0.7:
                            res = person.like()
                            print("LIKE")
                            print("Response: ", res)
                        else:
                            raise Exception("DISLIKE")
                    except Exception as ex:
                        print(ex)
                        res = person.dislike()
                        print("Response: ", res)

    classifier.close()
