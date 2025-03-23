import plotly.express as px
from dataclasses import dataclass

import unidecode

## Inputs

inputs = {
    'louis': [
        "Hector",
        "Timothée",
        "Adrien",
        "Achille",
        "Erwan",
        "Cyril",
        "Maël",
        "Florian",
        "Ulysse",
        "Antoine",
        "Clémence",
        "Claire",
        "Hortense",
        "Margaux",
        "Charlotte",
        "Diane",
        "Emma",
        "Juliette",
        "Philippine",
        "Maëlys",
    ],
    'cecile': [
        "Timothée",
        "Arthur",
        "Achille",
        "Victor",
        "Alexandre",
        "Théophile",
        "Jules",
        "Alexis",
        "Aurélien",
        "Gabriel",
        "Juliette",
        "Raphaëlle",
        "Alix",
        "Clémence",
        "Agathe",
        "Charlotte",
        "Alice",
        "Pénélope",
        "Daphnée",
        "Gabrielle",
    ],
    'maman': [
        "Marguerite",
        "Marguerite-Marie",
        "Marie-Charlotte",
        "Anne-Charlotte",
        "léopoldine",
        "Pia",
        "Philippa",
        "Philippine",
        "Léopoldine",
        "Diane",
        "Augustine",
        "Hortense",
        "Josephine",
        "Brune",
        "Paul",
        "léopold",
        "Calixte",
        "Amaury",
        "Vianney",
        "Honoré",
        "Octave",
        "Leonard",
        "Achille",
        "Henri",
        "Philibert",
        "Côme",
        "Stanislas",
    ],
    'victoire': [
        "Baptiste",
        "Gaspard",
        "Raphaël",
        "Côme",
        "Arthur",
        "Achille",
        "Alexandre",
        "Augustain",
        "Hugo",
        "Maxime",
        "Théodore",
        "Sergio",
        "Kevin",
        "Jeanne",
        "Hortense",
        "Olympe",
        "Marion",
        "Joséphine",
        "Clemence",
        "Pauline",
        "Agathe",
        "Diane",
        "Eleonore",
        "Fatoumata",
        "Elena",
        "Penelope",
        "Celeste",
        "Alexia",
        "Philippine",
        "Rosalie",
        "Astrid",
        "Ariane",
        "Laure",
        "Bianca",
        "Paola",
        "Adelaïde",
        "Athenaïs",
        "Castille",
    ],
    'charles': [
        "Hélène",
        "Fatoumata",
        "Léopoldine",
        "Alexandre",
        "Charles",
        "Paul",
        "Gaspard",
    ],
    'papa': [
        "Jeanne-Hortense",
        "Marie-Eugénie",
        "Aliénor",
        "Anne-Charlotte",
        "Leopoldine",
        "Pénélope",
        "Hortense",
        "Félicie",
        "Philomène",
        "Faustine",
        "Constance",
        "Léonie",
        "Marguerite",
        "Fatoumata",
        "Enguerrand",
        "Paul-Emile",
        "Balthazar",
        "Alphonse",
        "Henri",
        "Hippolyte",
        "leopold",
        "Amaury",
        "Anatole",
        "Gustave",
        "Hector",
        "Achille",
        "Côme",
        "Augustin",
        "Maxence",
        "Charles",
        "Paul",
        "Raphaël",
    ]
}

## Classes

class NameOccurence:
    def __init__(self, data: dict):
        self.data = data
        self.name_occurence = {}
        self.ingest_all_data()
        self.occurence_repartition = {}
        self.compute_occurence_repartition()

    def ingest_all_data(self):
        for human, names in self.data.items():
            self.ingest_names(names)

    def ingest_names(self, names: list):
        for name in names:
            if name not in self.name_occurence.keys():
                self.name_occurence[name] = 0
            self.name_occurence[name] += 1

    def biggest_name(self):
        biggest_name = max(self.name_occurence, key=self.name_occurence.get)
        return biggest_name, self.name_occurence[biggest_name]

    def compute_occurence_repartition(self):
        for value in self.name_occurence.values():
            if value not in self.occurence_repartition:
                self.occurence_repartition[value] = 0
            self.occurence_repartition[value] += 1

    def chart_occurence_repartition(self):
        x = sorted(self.occurence_repartition.keys())
        y = [self.occurence_repartition[key] for key in x]
        fig = px.line(
            x=x,
            y=y,
            labels={
                'x': 'Nombre de fois qu"un prénom est choisi',
                'y': 'Nombre de prénoms'
            },
            title='Occurence Repartition'
        )
        fig.show()

    def number_of_singleton(self):
        return sum(1 for count in self.name_occurence.values() if count == 1)

@dataclass
class NameScore:
    name: str
    global_occurence: int

@dataclass
class HumanScore:
    name: str
    ranked_names: list[NameScore]

    def average_occurence(self) -> float:
        total_occurence = 0
        for name in self.ranked_names:
            total_occurence += name.global_occurence
        return round(total_occurence / len(self.ranked_names), 2)

class HumanScoreGenerator:
    def __init__(self, data: dict, name_occurence: NameOccurence):
        self.data = data
        self.name_occurence = name_occurence
        self.human_scores = []
        self.generate()

    def generate(self):
        for human_name, names in self.data.items():
            ranked_names = [
                NameScore(name=name, global_occurence=self.name_occurence.name_occurence[name])
                for name in names
            ]
            self.human_scores.append(HumanScore(name=human_name, ranked_names=ranked_names))
        self.human_scores.sort(key=lambda x: x.average_occurence(), reverse=True)

    def pretty_print(self):
        for human_score in self.human_scores:
            print(f"{human_score.name}: {human_score.average_occurence()}")


class DataCleaner:
    @classmethod
    def clean(cls, data: dict):
        cleaned_data = {}
        for human_name, names in data.items():
            cleaned_data[human_name] = []
            for name in names:
                cleaned_data[human_name].append(cls.clean_string(name))
        return cleaned_data

    @staticmethod
    def clean_string(input_str):
        cleaned_str = input_str.lower()
        cleaned_str = cleaned_str.replace(' ', '').replace('-', '')
        cleaned_str = unidecode.unidecode(cleaned_str)
        return cleaned_str


## Main
cleaned_data = DataCleaner.clean(inputs)

name_occurence = NameOccurence(cleaned_data)
print(f"Best name: {name_occurence.biggest_name()}")
print(f"Nombre de singletons: {name_occurence.number_of_singleton()}")
name_occurence.chart_occurence_repartition()

human_score_generator = HumanScoreGenerator(data=cleaned_data, name_occurence=name_occurence)
human_score_generator.pretty_print()
