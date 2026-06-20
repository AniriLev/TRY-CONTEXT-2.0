# TRY-CONTEXT-2.0
#### Video Demo:  <https://youtu.be/De68rnELVZU>

#### Description:
This project is designed for learners who want to improve their English.
As an English teacher, the most frequent question I am asked is “What is the most comfortable way to learn vocabulary?”. But I am an English learner myself as well, and I understand the struggle of those who don’t possess a high level of the language. And it so happened that I do know how to improve vocabulary without monotonous hours of memorizing words. And the secret is 'CONTEXT'. Words should be alive; they should have some purpose, and the purpose is the information they deliver, so there is no better way than the context. Carrying this weight of knowledge, I decided to build a program to help learners. It takes new words and creates a sentence in order to make words 'alive' by showing how to use them. But showing the context is not enough to remember the words — one must understand them. So the program satisfies this need as well. Based on the sentence it has built, the program creates a question for the user to answer and checks its correctness.
In a nutshell, the idea of the application is ask a user to complete a form for words of different types (e.g. nouns, verbs, etc.), create a sentence and a question based on the sentence, and check the user’s answer.

#### The application has:

**f_project/**
    **app.py** - Flask backend handling routes, database interaction, and communication between templates and logic
    **learnt_voco.db** - database with voco(table with words and ids), context(table with sentences and ids), link(table with ids of words and sentences to link them)
    **main.py** - a file with the main logic of the project. There are functions: setup_db(to creat tables in database), main(...), gen_sentence(resieves dictionary of words, returns generated sentence and question), generate_sentence(creats a list of words based on a random sentence structure), check_sentence(heldles all the grammer in the sentence), generate_questions(generates a questio based on the list for the sentence generation), check_answer(checks how close the user's answer is to the correct answer)
    **README.md**
    **requirements.txt**
    **static/**
        _context.png_ - picture used for the site design
        _image.png_ - icon
        _styles.css_
    **templates/**
        _error.html_ - is displayed in case of inapropriate input
        _history.html_ - list of learnt word and created sentences
        _index.html_ - home page with a form for words
        _layout.html_
        _result.html_ - shows different content depending on corret and incorrect answers
        _sentence.html_ - displays the created sentence, question for the sentence and a form for user's answer

#### Technologies used:
- Python (Flask)
- SQLite
- Bootstrap
- spaCy (NLP)

#### How it works:
1.  After openning the home page of the web application, a user sees greetings as well as a self-introduction:
"Hi! I know the best way to learn new words is through CONTEXT. So try me out and see how well you can understand your newly learned words! I will create one sentence using the words you provide and ask one question. Your goal is to analyze the sentence and answer the question to check if you understand the CONTEXT. Let's start!".
The next is a little addition to the application rules: "The application uses default words (such as: cat, fish, eat, play, cute, at home, at night) if some words are not provided." This text is displayed on the main page: index.html. The greetings are followed by a form with different parts of speech for user to fill in.

2.  The form asks the user for words of each type: nouns(2 words), transitive verbs, intransitive verbs, adjectives, places, and times. However, if the user provides fewer than 2 words for nouns or does not provide words at all for some or any of the types, the program handles this too by putting default words: 'cat' and 'fish' for nouns, 'eat' for transitive verbs, 'play' for intransitive verbs, 'cute' for adjectives, 'at home' for places, and 'at night' for times. If the user enters more than 2 words, the program randomly chooses the necessary number of words for sentence building. After that, a dictionary with word types and input word lists is made. It's hendled by index route in app.py.

3.  After all words are gathered, the program send the dictionary to the main.py's gen_sentnece function. This function operates other functions in the main.py. The dictionary goes to generate_sentnece function where a sentence structure and the words that are necessary for this structure are randomly choosen. The function returns a list that carries mini-lists with words and their word types in the order they should appear in the sentence, based on the randomly chosen form.

4.  After this list goes to the function 'check_sentence', that apply grammar rules and finalize the sentnece. This function puts the article 'the' in front of nouns or adjectives with nouns, but not pronouns. It also handles subject-verb relations. After all the checks, the sentence is sent to generate_questions function.

5.  The next step is a question, and it is built by a function named 'generate_questions'. The function takes the sentence that has been made and, with the help of the library spaCy, makes a dictionary with the role of each word and the word in the sentence. After that, the function chooses a random question form and builds the list as in the function 'generate_sentence'. The same function then handles subject-verb relations. After the sentence and the question are ready they are sent back to index route and displayed on sentence.html page along with an answer form. Along with that the function db_insertion in app.py recieves a list of words that were used in the created sentence with their parts of speech and the generated sentence. This function records the words with their part of speech and the sentence they were used in into the learnt_voco database.

6.  After the user inputs their answer, the program checks is. This is done by the function 'check_answers'. This function takes the sentence, the question, and the dictionary of words and their types. The function receives the user’s answer from the form and compares it to previously prepared correct answers or with the original sentence if the answer does not look like either of the prepared ones. If the user’s answer does not match the prepared ones, then the function compares the answer with the original sentence using the function 'SequenceMatcher' from the built-in library 'difflib'. The logic of this correctness assessment is based on how close the answer is to the original sentence.

If the user’s answer is correct (or similarity is greater than 0.3 for usual sentences and 0.1 for sentences with 'Who'), through the sentence route congratulations are displayed on the page result.html. If the user’s answer is not correct, then the correct answer and some cheers are displayed on the page.
In reality, I did not have to use 'difflib' to check the answer; I could have used spaCy again, but I wanted to try a different approach.

7. If the user enters numeric input, the application redirects to error.html.
8. A user can get to home page and history page from any page of the website.
9. For the design I've used bootstrap.
10. I used ChatGPT as a learning and debugging assistant during development. All implementation decisions and final code structure are my own. Additionally, some images used in the UI (e.g. icons and design elements in the static folder) were generated using AI tools.
