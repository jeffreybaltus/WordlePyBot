#Wordle PyBot
#https://www.powerlanguage.co.uk/wordle/


#Import packages
import nltk
from nltk.corpus import words
#nltk.download()
import random
import pandas as pd
import os

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


#Gather potential words (5 letters in length) from corpus of words
wordle_dictionary = []
n = 0
for i in words.words():
    if len(i) == 5:
        wordle_dictionary.append(i.upper())
    n = n + 1


#Load 3000 most common words in English language
mcw = pd.read_excel (r'MostCommonWords.xlsx')
mcw = mcw['CommonWords'].tolist()


#Set-up prior to making any guesses
eligible_alphabet_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
eligible_dictionary = wordle_dictionary.copy()
letters_in_correct_spot = ''
letters_in_incorrect_spot = ''
guess_word = ''
guess_history = []
guess_likelihood_history = []


#Begin making guesses
for j in range(7):
    #Clear output to remove clutter
    clearConsole()
    
    #If beyond the 6 guesses, then PyBot has lost
    if j == 6:
        print()
        print('PyBot did not win the Wordle of the day. Here were PyBot''s guesses:')
        for gh in guess_history:
            print(gh)
        print()
        break
    
    print('Making guess #', j + 1, '. This is the list of letters available: ', eligible_alphabet_string)

    #Reset the current eligible dictionary from which we will build remaining eligible words to guess
    eligible_dictionary_cur = []

    #Counter for words in eligible_dictionary, loops through and verifies that they are still eligible
    w = 0
    for i in eligible_dictionary:

        #Assume eligible until not eligible
        eligible_flag = 1

        #Loops through letters in each potentially eligible word to determine eligibility status
        for c in range(5):
            #Removes words with letters that have been eliminated (i.e. gray letters)
            if i[c] not in eligible_alphabet_string:
                eligible_flag = 0
                break
            else:
                eligible_flag = 1
            if eligible_flag == 0:
                break
            
            #Removes words without letters in correct spot (i.e. green letters)
            if len(letters_in_correct_spot) > 0:
                for cs_pos in letters_in_correct_spot:
                    if i[int(cs_pos) - 1] == guess_word[int(cs_pos) - 1]:
                        eligible_flag = 1
                    else:
                        eligible_flag = 0
                    if eligible_flag == 0:
                        break
                if eligible_flag == 0:
                    break

            #Removes words with letters in incorrect spot to ensure PyBot doesn't keep making the same wrong guess (i.e. yellow letters)
            if len(letters_in_incorrect_spot) > 0:
                for y in letters_in_incorrect_spot:
                    letter_to_keep = guess_word[int(y) - 1]
                    if letter_to_keep not in i:
                        eligible_flag = 0
                        break
                    else:
                        eligible_flag = eligible_flag
                    
                    if i[int(y) - 1] == guess_word[int(y) - 1]:
                        eligible_flag = 0
                        break

        #If this word is still eligible, then add it to the current dictionary from which to pick the next guess
        if eligible_flag == 1:
            eligible_dictionary_cur.append(eligible_dictionary[w])
        w = w + 1
        

    print('Total Possibilities Remaining: ', len(eligible_dictionary_cur))

    #Suggest answer from remaining possibilities
    was_correct_guess = 'X'
    sug_ans = 0
    guess_dict = {}
    guess_likelihood = 0.00
    while was_correct_guess == 'X':

        #Which valid guess has the most unique letters in common with other valid guesses?
        #Note: will only rank possibilities once for the first guess due to time/performance constraint
        if (j == 0) and (sug_ans == 0):
            for edc in eligible_dictionary_cur:
                if edc in mcw:
                    guess_dict[edc] = 1
        else:
            guess_dict = {}
            for a in eligible_dictionary_cur:
                d = 0
                for b in list(set(a)):
                    for c in eligible_dictionary_cur:
                        if b in c:
                            d = d + 1
                #Prioritize potential guesses that are in most common words
                if a in mcw:
                    d = (d + 1) * 3
                guess_dict[a] = d
        
        #Sort the count of commonality by most likely to least common
        guess_dict = dict(sorted(guess_dict.items(), key = lambda x: x[1], reverse = True))
        
        #Select top 10 pct of guesses (by commonality, not necessarily count of words)
        top_10_pct_guess = []
        for i in guess_dict:
            if guess_dict.get(i) >= guess_dict.get(list(guess_dict.keys())[0]) * 0.95:
                top_10_pct_guess.append(i)

        #Pick random guess from the top 10 pct of guesses
        guess_word = random.choice(top_10_pct_guess)
        guess_likelihood = round(guess_dict.get(guess_word) / sum(guess_dict.values()), 4)
        print('Try guessing: ', guess_word, ' (', guess_likelihood, '% likelihood)')
        sug_ans = 1
        
        #Initial user feedback about whether the guess was valid or not
        print()

        was_correct_guess = input("Was this the correct guess? (Enter Y or N; or X if an invalid guess): ")
        was_correct_guess = was_correct_guess.upper()
        
        if was_correct_guess != 'X':
            break
        else:
            #If guess was not valid, remove the guess from eligible words and try again
            eligible_dictionary.remove(guess_word)
            eligible_dictionary_cur.remove(guess_word)
            del guess_dict[guess_word]
        
    
    #Add guess to guess history
    guess_history.append(guess_word)
    guess_likelihood_history.append(guess_likelihood)
    
    #Was the Wordle of the day guessed?
    if was_correct_guess == 'Y':
        clearConsole()
        print()
        print('*************************************************')
        print('CONGRATULATIONS, PyBot WON THE WORDLE OF THE DAY!')
        print('*************************************************')
        print()
        print('It took PyBot ', j + 1, ' guesses!')
        print()
        print('PyBot''s guess history was:')
        for gh in guess_history:
            print(gh)
        break

    #If guess was not Wordle of the day, gather user feedback about gray, green, and yellow boxes
    guess_colors = input("What was the resulting colors? (Enter: X for grey; G for green; and Y for yellow): ")
    guess_colors = guess_colors.upper()
    letters_not_eligible = ''
    letters_in_correct_spot = ''
    letters_in_incorrect_spot = ''
    color_counter = 1
    for gc in guess_colors:
        if gc == 'X':
            letters_not_eligible = letters_not_eligible + str(color_counter)
        if gc == 'G':
            letters_in_correct_spot = letters_in_correct_spot + str(color_counter)
        if gc == 'Y':
            letters_in_incorrect_spot = letters_in_incorrect_spot + str(color_counter)
        color_counter = color_counter + 1
        
    
    #Fix potential issue of logging multiple letter guesses incorrectly
    #E.g., if the guess 'SPOON' had a green 'O' in spot 3 and gray in spot 4, we don't want to remove 'O' from eligible alphabet
    letters_in_answer = letters_in_correct_spot + letters_in_incorrect_spot
    letters_in_answer_2 = []
    for lia in letters_in_answer:
        letters_in_answer_2.append(guess_word[int(lia) - 1])
    for x in letters_not_eligible:
        remove_letter = guess_word[int(x)-1]
        if remove_letter in letters_in_answer_2:
            remove_letter = ''
        eligible_alphabet_string = eligible_alphabet_string.replace(remove_letter.upper(), '')
    
    #If guess was not correct, remove the guess from eligible words
    eligible_dictionary_cur.remove(guess_word)

    #Ensure that the eligible dictionary is not reset entirely to the full wordle_dictionary
    #This fixes the potential issue of yellow box guesses returning a similar (incorrect) yellow box guess
    eligible_dictionary = eligible_dictionary_cur.copy()
