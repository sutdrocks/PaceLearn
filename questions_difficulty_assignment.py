import pandas as pd

grammar_questions = pd.read_excel("Grammar Questions.xlsx")

mapping = {"A2":1 , "B1":2, "B2":3, "C1":4, "C2":5}

def change(alp_diff):
    return mapping[alp_diff]


grammar_questions["Numeric_difficulty"] = grammar_questions["Difficulty"].apply(change)

grammar_questions.to_excel("Grammar Questions.xlsx")