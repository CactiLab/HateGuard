# Please download necessary dependencies before running the code.
# !pip install keybert
# !pip install pyenchant==3.0.0a1
# !apt-get install enchant-2

import pandas as pd
import sys
import random
import enchant
import requests

from datetime import datetime
from keybert import KeyBERT

# You need to pass the input file and the date (month and year) when the term needs to be extracted
input_file = sys.argv[1]
month = int(sys.argv[2])
year = int(sys.argv[3])


data = pd.read_csv(input_file)

kw_model = KeyBERT()

def get_key_terms(text):
  keywords = kw_model.extract_keywords(text)
  terms = ''
  for word, conf in keywords:
    if conf > 0.5:
      terms = terms + ' ' + word
  return terms

# get the data that are hateful
data_hate = data[data['ground_truth']==1]

def is_english_word(word):
    d = enchant.Dict("en_US")
    return d.check(word), d.suggest(word)

def is_urban_word(word, date_key):
    url = f"https://api.urbandictionary.com/v0/define?term={word}"
    response = requests.get(url)
    data = response.json()
    if data['list']:
        when = data['list'][0]['written_on']

        # check if the word is a new term or not
        if datetime.strptime(when, "%Y-%m-%dT%H:%M:%S.%fZ") < date_key:
            return False
        else:
            return True
    else:
        return True
    time.sleep(1)

# function to extract keywords
def keyword_extract(data, month, year):
  # get keywords
  terms = set()
  for i in range(5):
    random_number = random.randint(10, 20)
    try:
      data_seed = data.sample(n = random_number)
    except:
      continue

    for date, text, gt in zip(data_seed['month'].tolist(), data_seed['original_text'].tolist(), data_seed['ground_truth'].tolist()):
      if date == month:
        if gt == 1:
          keywords_text = get_key_terms(text)
          for word in keywords_text.split():
            terms.add(word)
  terms = list(terms)
  print("\nKeywords found:\n", terms)

  new_derog_terms = set()
  for word in terms:
    if word.isnumeric():
      continue

    cleaned_word = ''.join(letter for letter in word if letter.isalnum())
    if cleaned_word != '':
      present, suggs = is_english_word(cleaned_word)
    else:
      present = True
    if not present:
        new_derog_terms.add(cleaned_word)
  new_derog_terms = list(new_derog_terms)
  # print("\n",new_derog_terms)

  final_set = set()
  for word in new_derog_terms:
      if is_urban_word(word, datetime.strptime(f'{year}-{month}-1', '%Y-%m-%d')):
          final_set.add(word)
  final_terms = list(final_set)
  print("The final terms are:", final_set)
  return final_terms

# get the keywords
results = keyword_extract(data_hate, month, year)
print("\n\n\nThe final terms are:", results)

# save the results
with open(f'terms_{month}_{year}.txt', 'w') as f:
  for item in results:
    f.write("%s\n" % item)

print("The terms are saved in terms_{month}_{year}.txt file")

