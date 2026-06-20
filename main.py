import random
import spacy
from difflib import SequenceMatcher
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///learnt_voco.db")


def setup_db():
    # table for inputed words and thier pos
    db.execute("""
               CREATE TABLE IF NOT EXISTS voco (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               word TEXT UNIQUE NOT NULL,
               part_of_speach TEXT NOT NULL
               )
               """)

    # table for sentences with the words from the first table
    db.execute("""
               CREATE TABLE IF NOT EXISTS context (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               sentence TEXT UNIQUE NOT NULL
               )
               """)

    # linking ids between voco and sentence tables
    db.execute("""
               CREATE TABLE IF NOT EXISTS link (
               word_id INTEGER,
               sentence_id INTEGER,
               FOREIGN KEY (word_id) REFERENCES voco(id),
               FOREIGN KEY (sentence_id) REFERENCES context(id),
               PRIMARY KEY (word_id, sentence_id)
               )
               """)

def main():

    items = {"nouns":['cat', 'fish'], "transitive_verbs":['eat', 'hit'], "intransitive_verbs":['laugh', 'run'], "adjectives":['cool', 'funny'], "places":['at work', 'in the forest'], "times":['at night', 'on fryday']}
    sentence_text, question, context, sent_list = gen_sentence(items)
    us_answer = input("Put your answer here: ")

    ans = check_answers(sentence_text, question, context, us_answer)
    if ans == "Correct":
        print("Nice! Found a new word? Welcome to try more!")
    else:
        print("Don't worry! You are always welcome to try more!")

def gen_sentence(words_input):
    setup_db()

    sentence = generate_sentence(words_input)

    sen = check_sentence(sentence)
    qus, ans_itms = generate_questions(sen)

    return sen, qus, ans_itms, sentence

def generate_sentence(used_words):

    sen_structure = ["adjectives nouns transitive_verbs nouns places times", "adjectives nouns intransitive_verbs places times", "nouns intransitive_verbs places times"]
    structure = random.choice(sen_structure).split(" ")

    sentence_list = []

    for part_of_speach in structure:
        word = used_words[part_of_speach].pop(random.randrange(len(used_words[part_of_speach])))
        sentence_list.append((word, part_of_speach))

    return sentence_list

def check_sentence(sentence):
    pronouns = ["he", "she", "i", "it", "you", "we", "they"]
    pos_pronouns = {"he":"his", "she":"her", "i":"my", "it":"its", "you":"your", "we":"our", "they":"their"}
    obj_pronouns = {"he":"him", "she":"her", "i":"me", "it":"it", "you":"you", "we":"us", "they":"them"}

    new_sentence = []

    for i, (word, part) in enumerate(sentence):
        prev = sentence[i-1] if i > 0 else (None, None)
        nxt  = sentence[i+1] if i+1 < len(sentence) else (None, None)
        prev_word, prev_part = prev
        next_word, next_part = nxt

        # 1. Артикли и притяжательные местоимения
        if word not in pronouns:
            if part == "adjectives" and next_part == "nouns" and next_word not in pronouns:
                new_sentence.append("the")
            elif part == "nouns" and prev_part not in ["adjectives", "nouns"] and next_part != "nouns":
                new_sentence.append("the")
        else:
            if next_part == "nouns" and next_word not in pronouns:
                word = pos_pronouns[word]

        # 2. Объектные местоимения (he -> him)
        if word in pronouns and prev_part in ["intransitive_verbs", "transitive_verbs"]:
            word = obj_pronouns[word]

        # 3. Согласование подлежащего и сказуемого
        if part in ["intransitive_verbs", "transitive_verbs"] and prev_part == "nouns":
            if word == "be":
                if prev_word == "i":
                    word = "am"
                elif prev_word.endswith("s"):
                    word = "are"
                else:
                    word = "is"
            elif (prev_word not in ["i", "you", "they", "we"] and not prev_word.endswith("s")) or prev_word in ["he", "she", "it"] :
                if word.endswith(("s", "sh", "ch", "x", "o", "z")):
                    word += "es"
                elif word.endswith("y") and word[-2] not in "aeuio":
                    word = word[:-1] + "ies"
                else:
                    word += "s"

        # 4. Пропуск прилагательного перед местоимением
        if part == "adjectives" and next_word in pronouns:
            if new_sentence and new_sentence[-1] == "the":
                new_sentence.pop()
            continue

        new_sentence.append(word)

    final_sentence = " ".join(new_sentence).capitalize()

    return final_sentence

#Sentences are ready, now it is time for questions
nlp = spacy.load("en_core_web_sm")

def generate_questions(sentence):

    doc = nlp(sentence)

    doc_list = []
    for token in doc:
        doc_list.append((token.text, token.dep_, token.head.text, token.ent_type_))


    sp_parts = ["compound", "nsubj", "ROOT", "dobj", "place", "time"]
    sec_prep = {}

    for word, part, link, add in doc_list:
        if part in sp_parts:
            sec_prep[part] = word

        if add in ["DATE", "TIME"]:
            sec_prep["time"] = f"{link} {word}"

        if add == '' and part == "pobj":
            sec_prep["place"] = f"{link} {word}"

    if 'nsubj' in sec_prep:
        subj=sec_prep['nsubj']
    elif 'compound' in sec_prep:
        subj=sec_prep['compound']

    root = sec_prep['ROOT']
    time = sec_prep.get('time', 'at night')
    place = sec_prep.get('place', 'at home')

    question_type_do = [f"Who {root} {time}?",
                        f"Where does {subj} {root} {time}?",
                        f"When does {subj} {root} {place}?",
                        f"What does {subj} do {place} {time}?"]
    question_type_be = [f"Who is {place} {time}?",
                        f"Where {root} {subj} {time}?"]

    question = []
    if root in ["am", "is", "are"]:
        type = random.choice(question_type_be)
        t_type = type.lower().split(" ")
        for word in t_type:
            question.append(word)

    else:
        type = random.choice(question_type_do)
        t_type = type.lower().split(" ")
        for word in t_type:
            if word == "does":
                if (subj.lower() in ["i", "they", "we", "you"] or subj.lower()[-1] == "s"):
                    question.append("do")
                else:
                    question.append("does")

            elif word == root and ("does" in question or "do" in question):
                if root.endswith(("ses", "shes", "ches", "xes", "oes", "zes", "ies", "s")):
                    if root.endswith(("ses", "shes", "ches", "xes", "oes", "zes")):
                        question.append(root[:-2])

                    elif root.endswith("ies"):
                        question.append(root[:-3] + "y")

                    elif root.endswith("s"):
                        question.append(root[:-1])
                else:
                    question.append(word)

            elif word == root and "who" in t_type  and ("does" not in question or "do" not in question):
                if root.endswith(("ses", "shes", "ches", "xes", "oes", "zes", "ies", "s")):
                    question.append(root)
                else:
                    if root.endswith(("s", "sh", "ch", "x", "o", "z")):
                        question.append(root + "es")

                    elif root.endswith("y") and root[-2] not in "aeuio":
                        question.append(root[:-1] + "ies")

                    else:
                        question.append(root + "s")

            else:
                question.append(word)

    give = " ".join(question).capitalize()
    return give.replace(" i ", " I "), sec_prep


def check_answers(sentence, question, words, us_answer):

    question = question.lower()
    sentence = sentence.lower()

    if 'nsubj' in words:
        subj = words['nsubj']
    elif 'compound' in words:
        subj = words['compound']

    if 'time' in words:
        time = words['time']
    else:
        time = 'at night'

    if 'place' in words:
        place = words['place']
    else:
        place = 'at home'

    sub_only = f"{subj}"
    time_only = f"{time}"
    verb_only = f"{words['ROOT']}"
    place_only = f"{place}"
    sub_verb = f"{subj} {words['ROOT']}"
    sub_verb_time = f"{subj} {words['ROOT']} {words['time']}"
    sub_verb_place = f"{subj} {words['ROOT']} {words['place']}"

    answer_rules = {
    "who":   {"correct": sub_only.lower(), "fallback": sub_verb_time, "threshold": 0.1},
    "when":  {"correct": time_only, "fallback": sub_verb_time, "threshold": 0.3},
    "what":  {"correct": verb_only, "fallback": sub_verb, "threshold": 0.3},
    "where": {"correct": place_only, "fallback": sub_verb_place, "threshold": 0.3},
    }


    us_answer = us_answer.lower()
    sim = SequenceMatcher(None, sentence, us_answer).ratio()

    for q_word, q_dict in answer_rules.items():
        if q_word in question:
            if q_dict['correct'] in us_answer:
                if us_answer == q_dict['correct'] or sim >= q_dict['threshold']:
                    return "Correct"
            else:
                return (f'{q_dict['fallback'].capitalize()}.')


if __name__=="__main__":
    main()

