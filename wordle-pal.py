from WordList.WordList import Words

words = Words()

for letter, count in words.soutionLetterCounterByFrequency.items(): print(f'{letter} : {count}')
print('--------------')
for letter, count in words.soutionLetterCounterByLetter.items(): print(f'{letter} : {count}')
