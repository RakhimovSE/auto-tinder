from time import time

import tensorflow as tf

from config import TOKEN
from tinder_api import TinderAPI
from likeliness_classifier import Classifier
import person_detector


if __name__ == "__main__":
    api = TinderAPI(TOKEN)

    detection_graph = person_detector.open_graph()
    with detection_graph.as_default():
        with tf.Session() as sess:

            classifier = Classifier(graph="./tf/training_output/retrained_graph.pb",
                                    labels="./tf/training_output/retrained_labels.txt")

            end_time = 1568992917 + 60*60*2.8
            while time() < end_time:
                try:
                    print(f"------ TIME LEFT: {(end_time - time())/60} min -----")
                    persons = api.nearby_persons()
                    pos_schools = ["Universität Zürich", "University of Zurich", "UZH", "HWZ Hochschule für Wirtschaft Zürich",
                                   "ETH Zürich", "ETH Zurich", "ETH", "ETHZ", "Hochschule Luzern", "HSLU", "ZHAW",
                                   "Zürcher Hochschule für Angewandte Wissenschaften", "Universität Bern", "Uni Bern",
                                   "PHLU", "PH Luzern", "Fachhochschule Luzern", "Eidgenössische Technische Hochschule Zürich"]

                    for person in persons:
                        score = person.predict_likeliness(classifier, sess)

                        for school in pos_schools:
                            if school in person.schools:
                                print()
                                score *= 1.2

                        print("-------------------------")
                        print("ID: ", person.id)
                        print("Name: ", person.name)
                        print("Schools: ", person.schools)
                        print("Images: ", person.images)
                        print(score)

                        if score > 0.8:
                            res = person.like()
                            print("LIKE")
                            print("Response: ", res)
                        else:
                            res = person.dislike()
                            print("DISLIKE")
                            print("Response: ", res)
                except Exception:
                    pass




    classifier.close()
