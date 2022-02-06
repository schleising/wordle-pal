from WordList.WordList import Words

words = Words()

print(f'Number of Solutions   : {len(words.solutionWordlist)}')
print(f'Number of Valid Words : {len(words.validWordList)}')
print()
print(f"Today's Word is       : {words.todaysWord}")
