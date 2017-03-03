
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2016
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
# Ported to Java by Raghav Gupta (@rgupta93) and Jennifer Lu (@jenylu)
######################################################################
import csv
import math

import numpy as np

from movielens import ratings
from random import randint
from pprint import pprint
import re
import random
import numpy
import copy
import warnings
warnings.filterwarnings("ignore")

# TODOs:
# Modify asking about genres
# Debug
# Say different things about movies in one line

class Response:

    def __init__(self, things, sentiment, sentimentWords):
        self.things = things
        self.sentiment = sentiment
        self.words = sentimentWords


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    punc = [",", "!", ".", ";", "?", "but", "yet"]
    negationWords = ['never', 'haven\'t', 'hadn\'t', 'not', 'nor',
                     "n't", "didn't", "wasn't", "don't", "dont", "didnt", "wasnt"]

    ##########################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    ##########################################################################
    def __init__(self, is_turbo=False):
        self.name = 'Charlie'
        self.is_turbo = is_turbo
        self.read_data()
        self.genres = set([])
        for title in self.titles:
            for genre in title[1].split('|'):
                self.genres.add(genre.lower())

        self.userPrefs = {'genres': {}, 'movies': {}}

        self.deixis = None

        self.recommendedGenres = []

        self.askAboutEmotion = 1
        self.askAboutMovies = True
        self.askAboutGenres = False
        self.giveRecs = False
        self.firstTimeAskAboutGenres = True

    def respondToEmotion(self, words, sentiment):
        """Return a catch-all response about some sentiment which is not associated with any movie or genre.
        Then, suggest to the user to go back to the topic of movies/genres."""
        self.askAboutEmotion += 1

        word = random.choice(
            [w for w in words if not w.lower() in self.genres])
        wordSentiment = self.sentiment.get(word)
        if word in ["like", "love", "hate", "dislike", "enjoy"]:
            return random.choice(["What do you %s about it?",
                                  "Why do you %s it?",
                                  "What makes you %s it?",
                                  ]) % word + self.addendumMild()
        if word in ["liked", "loved", "hated", "disliked", "enjoyed"]:
            return random.choice(["What did you %s about it?",
                                  "Why did you %s it?",
                                  "What made you %s it?",
                                  ]) % word + self.addendumMild()
        else:
            newWord = word
        if sentiment > 0:
            if wordSentiment == 'neg':
                newWord = 'not ' + word
            if word.lower() in ['great', 'awesome', 'fun', 'cool', 'amazing', 'interesting', 'fascinating', 'good']:
                sent = random.choice(["I am not sure what is %s in your opinion. Please explain.",
                                      "What makes you feel it is %s?",
                                      "And what makes it so %s?",
                                      "Is there any particular reason you feel it is %s?",
                                      ]) % newWord + self.addendumMild()
            elif word.lower() in ['happy', 'glad', 'satisfied', 'curious']:
                sent = random.choice(["I am not sure what you are %s about. Please explain.",
                                      "What makes you feel %s?",
                                      "And how does it feel to be %s?",
                                      "Is there any particular reason you feel %s?",
                                      ]) % newWord + self.addendumMild()
            else:
                sent = random.choice(["I am happy to hear you feel that way.",
                                      "I am glad you feel that way.",
                                      "That is good to hear.",
                                      "Ok, that's good.",
                                      "I appreciate you sharing it with me."]) + self.addendum()

            return sent
        if sentiment < 0:
            if wordSentiment == 'pos':
                newWord = 'not ' + newWord

            if word.lower() in ['bad', 'annoying', 'boring', 'miserable', 'stupid', 'ridiculous', 'uninteresting', 'pointless']:
                sent = random.choice(["I am not sure what is %s in your opinion. Please explain.",
                                      "What makes you feel it is %s?",
                                      "And what makes it so %s?",
                                      "Is there any particular reason you feel it is %s?",
                                      ]) % newWord + self.addendumMild()
            elif word.lower() in ['sad', 'angry', 'unhappy', 'upset', 'bored']:
                #"Is there anything I can do to make you not %s?"
                sent = random.choice(["I am not sure what you are %s about. Please explain.",
                                      "What makes you feel %s?",
                                      "Thank you for sharing this with me. We can continue this discussion if you want."
                                      "I am sorry to hear you are %s! Feel free to tell me more about it.",
                                      "And how does it feel to be %s?",
                                      "Is there any particular reason you feel %s?",

                                      ]) % newWord + self.addendumMild()
            else:
                sent = random.choice(["I am sorry to hear you feel that way.",
                                      "That is not so good to hear.",
                                      "I am sorry to hear that. Would you like to elaborate?",
                                      "Ok, gotcha.",
                                      "I appreciate you sharing it with me."]) + self.addendum()
            return sent

    def askForClarification(self):
        self.askAboutEmotion += 1

        return random.choice(["Sorry, I didn't get that. Can you say it again?",
                              "Sorry, I missed that. Can you say it differently?",
                              "I am sorry, but I'm not sure what you meant. Please say it again."]) \
            + self.addendumMild()

    def addendum(self):
        "Add a generic response that attempts to get the user to go back to the topic of giving the system ratings."
        if self.askAboutGenres or self.askAboutMovies:
            if self.askAboutGenres:
                morg = "genres"
            elif self.askAboutMovies:
                morg = "movies"

            return " %s %s." % (random.choice(["We can also go back to discussing",
                                               "Actually, if you don't mind, let's go back to",
                                               "I suggest we go back to",
                                               "I think the best idea right now, if it's fine with you, would be going back to",
                                               "But in fact I am mostly good for movie recommendations, so if that's okay let's talk about some more"]),
                                morg)
        else:
            return ''

    def addendumMild(self):
        "Like self.addendum, only more gentle."
        if self.askAboutGenres or self.askAboutMovies:
            if self.askAboutGenres:
                morg = "genres"
            elif self.askAboutMovies:
                morg = "movies"

            return "%s %s." % (random.choice([" Or we can also go back to discussing",
                                              " Or we can simply back to",
                                              " Or we can also go back to",
                                              " Or we can also go back to talking about",
                                              " Or we could return to",
                                              " Or we go back to talking about",
                                              " Or we could go back to", ]), morg)
        else:
            return ''

    ##########################################################################
    # 1. WARM UP REPL
    ##########################################################################

    def greeting(self):
        """chatbot greeting message"""
        #######################################################################
        # TODO: Write a short greeting message                                      #
        #######################################################################

        greeting_message = \
            'Hello, my name is Charlie. I am here to recommend movies for you. Tell me about some movies and what you think about them.' \
            '\nPlease wrap any movie title by double quotation marks, and make sure movie names are capitalized correctly.'  # We are going to only allow double quotation marks

        #######################################################################
        #                             END OF YOUR CODE                              #
        #######################################################################

        return greeting_message

    def isQuestion(self, line):
        "Find out if a line looks like a question."
        words = line.split(' ')
        return words[0].lower() in "tell is are am who what where when will can should would is do".split(' ') or line[-1] == '?'

    def processQuestion(self, line):
        "Give a generic answer to a question."

        response = ''
        line1 = copy.copy(line)
        line2 = copy.copy(line)
        extractMovies = self.extractMovies(line1)
        # Get the movies mentioned in the question (self.extractMovies returns
        # a tuple (Response, warnings)
        movies = extractMovies[0].things
        warnings = extractMovies[1]
        for warning in warnings:
            response += warning + "\n"  # Add any warnings about wrong years to the response
        genres = self.extractGeneres(line2).things  # Get the genres
        if movies and genres:
            # Choose randomally between the two
            response += random.choice([self.processQuestionGenres(genres),
                                       self.processQuestionMovies(movies)])
        elif movies and not genres:
            response += self.processQuestionMovies(movies)
        elif genres and not movies:
            response += self.processQuestionGenres(genres)
        else:
            response += random.choice(["Unfortunately this question is beyond my ability to answer.",
                                       "I am sorry, I do not support answering these question.",
                                       "I am unable to provide this kind of information. Apologies.",
                                       "I apologize, but I am unable to answer such questions. I can however give you some information about specific movies or genres if you want!"])
        if self.askAboutGenres:
            morg = "genres"
        elif self.askAboutMovies:
            morg = "movies"
        else:
            return response + "\nIs there anything else %s?" % random.choice(["you would like to know", "I can help you with", "I can help with"])
        return response + "\nIs there anything else %s? %s" % (random.choice(["you want to ask", "you would like to know", "I can help you with", "I can help with"]),
                                                               self.addendum())

    def processQuestionMovies(self, movies):
        "Gives some basic information about a randomally selected movie and encourages the user to go back to the real topic."
        moviesNew = numpy.random.permutation(
            movies)  # Randomally rearrange the movies
        for movie in moviesNew:
                # For each movie, look for it in the database
            for title in self.titles:
                # If it is a spelling variant of some movie in the database,
                if movie in self.handleArticle(title[0][:-7]):
                    # Get all of its genres
                    genre = random.choice(title[1].split('|'))
                    if genre[0].lower() in 'aeiou':  # Modify the article
                        article = 'an'
                    else:
                        article = 'a'
                    year = re.findall('\((\d\d\d\d)\)', title[0])[
                        0]  # Get the year
                    # And tell the user this information:
                    return random.choice(["All I can say is that \"%s\" is %s %s movie from %s. I am sorry if this does not answer your question.",
                                          "According to my database, \"%s\" is %s %s movie from %s.",
                                          "Well, I can tell you that \"%s\" is %s %s movie from %s."
                                          ]) % (movie, article, genre, year)
        # If no movie found in the database, say so.
        return "I have no data about %s. Apologies." % self.conjPhraseFromList(movies, True)

    def processQuestionGenres(self, genres):
        "Gives some basic information about a genre mentioned in a question."
        genresNew = numpy.random.permutation(genres)

        for genre in genresNew:

            sampleMovies = self.conjPhraseFromList(numpy.random.permutation(
                [title[0] for title in self.titles if genre in title[1].lower()][:3]), True)
            for title in self.titles:
                if genre.lower() in title[1].lower().split('|'):
                    return random.choice(["I can say that some examples of %s movies are %s. I am sorry if this does not answer your question.",
                                          "In my database there are some %s movies such as %s. This is all the information I can give you in this matter.",
                                          "Some of the %s movies found in my database are %s. This is all I know in this regard.",
                                          "Well, all I can I tell you that some %s movies are for example %s.",
                                          ]) % (genre, sampleMovies)

    def goodbye(self):
        """chatbot goodbye message"""
        #######################################################################
        # TODO: Write a short farewell message                                      #
        #######################################################################

        goodbye_message = 'Happy to be of service. Till the next time!'

        #######################################################################
        #                             END OF YOUR CODE                              #
        #######################################################################

        return goodbye_message

    ##########################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    ##########################################################################

    deicticals = "it them they those these that this".split()

    def contains(self, line, words):
        return [word in line for word in words]

    def getDataMovies(self):
        return self.userPrefs['movies'].keys()

    def getNumDataMovies(self):
        return len(self.getDataMovies())

    def getDataGenres(self):
        return self.userPrefs['genres'].keys()

    def getNumDataGenres(self):
        return len(self.getDataGenres())

    def process(self, input):
        """Takes the input string from the REPL and call delegated functions
        that
          1) extract the relevant information and
          2) transform the information into a response to the user
        """
        #######################################################################
        # TODO: Implement the extraction and transformation in this method, possibly#
        # calling other functions. Although modular code is not graded, it is       #
        # highly recommended                                                        #
        #######################################################################
        response = ''

        # I like "Avatar", "La Bamba" and "The Matrix" (1999)

        # Add NOT_ before any negated word
        words = input.split()
        inNegScope = False
        for i in range(len(words)):
            tok1 = words[i]
            if tok1.lower() in self.negationWords:
                inNegScope = True
            if tok1 in self.punc:
                inNegScope = False

            if inNegScope and not tok1 in self.negationWords:
                words[i] = "NOT_" + tok1
        input = ' '.join(words)

        if self.isQuestion(input):
            # If the input is recognized as a question
            return self.processQuestion(input)

        else:

            verb = None  # Whether the sentiment is positive or negative

            # If the bot is now processing movie rating
            if self.askAboutMovies:
                # decompose the input line into its components
                userResponse, warnings = self.extractMovies(input)
                for warning in warnings:
                    response += warning  # Add each warning to the bot's eventual response
                # These are the components extracted by
                movies, sentiment, sentimentWords = userResponse.things, userResponse.sentiment, userResponse.words
                # self.extractMovies
                # If the bot remembers reference to an unrated movie from a
                # previous line,
                if self.deixis and not movies and self.contains(input, self.deictcals):
                                                                                       # and no new movies are mentioned in this line, and this line contains
                                                                                       # a deictical expression (such as 'it','this','that').
                                                                                       # For example, if the user typed 'I watched "The Matrix"', then the bot remembers
                                                                                       # "The Matrix" but it doesn't know what is the user's ranking. Now, the bot memorizes
                                                                                       # "The Matrix" in the self.deixis field, and when the user says something with a
                                                                                       # deictical
                                                                                       # expression,
                                                                                       # the
                                                                                       # bot
                                                                                       # assumes
                                                                                       # it
                                                                                       # refers
                                                                                       # to
                                                                                       # the
                                                                                       # movie.
                    movies = self.deixis  # define the movies variable to be the memorized deixis
                # If the bot found any movies, it will add to the response the
                # echo of those movies:
                if movies and not sentiment:
                    # The bot is not sure what the user thinks about these
                    # movies and so asks for clarification and saves them in
                    # the self.deixis field
                    self.deixis = movies
                    response += "I am not sure what your opinion is about %s. Can you clarify?" % self.conjPhraseFromList(
                        movies)
                elif sentiment and not movies:
                    # If there is sentiment expressed without reference to a movie, the bot makes some kind of response and then suggests
                    # to return to the topic of movies
                    if (float(self.askAboutEmotion) / 6.0).is_integer():
                        # this is for variety; after 5 responses to emotion,
                        # the bot asks clarification
                        response += self.askForClarification()
                    else:
                        # respond according to the emotion expressed in the
                        # input line
                        response += self.respondToEmotion(
                            sentimentWords, sentiment)
                elif movies:
                    # If there is both movies and sentiment; this is the main
                    # part of this code
                    self.deixis = None  # reset the deixis field
                    # the genres of all the user's rated movies before any
                    # changes that happen in this block
                    userGenresOld = self.userGenres()
                    prevSame = []  # Already rated movies with unchanged rating
                    prevDiff = []  # Already rated movies with changed rating
                    # all the movies in the input line which are in the bot's
                    # database
                    indb = self.titlesWithoutYear.intersection(movies)
                    for movie in indb:
                        if self.titlesDict[movie] in self.userPrefs['movies'].keys():
                            # If the movie is already in the user's preferences
                            # dictionary, populate the prev lists accordingly:
                            if self.userPrefs['movies'][self.titlesDict[movie]] == sentiment:
                                prevSame.append(movie)
                            else:
                                prevDiff.append(movie)
                        # This is the line where the user's preferences are
                        # recorded
                        self.userPrefs['movies'][
                            self.titlesDict[movie]] = sentiment
                        # self.userPrefs is the dictionary which the bot uses to
                        # perform collaborative filtering based on the user's
                        # preferences
                    unkString = ''
                    if indb != set(movies):
                        # The set of movies mentioned by the user which are not
                        # in the bot's database
                        unks = [movie for movie in movies if not movie in indb]
                        # Explain that the bot has no data about these movies:
                        unkString += ' Unfortunately, I do not have data about ' + self.conjPhraseFromList(unks) + ','\
                            'so I will not be able to take them into account in my recommendation.'

                    # Create a string which represents the list of movies
                    moviesString = self.conjPhraseFromList(movies, True)

                    # Mention it if the bot aleady has information about some
                    # movies:
                    if prevSame:
                        response += random.choice(["Well, I already had this information about %s.",
                                                   "Yes, I am aware of your opinion about %s.",
                                                   "Your rating of %s is already registered in the system, thank you."]) % self.conjPhraseFromList(prevSame, True)

                    if prevDiff:
                        response += random.choice(['I am revising your opinion about %s... Done. ',
                                                   'Gotcha, updating your listed rating of %s... Done. ',
                                                   'Right, so you\'re giving me a new opinion on %s. I\'m updating your data... Done. '
                                                   ]) % self.conjPhraseFromList(prevDiff, True)

                    # According to the sentiment, add a verb to the response
                    if sentiment > 1:
                        verb = 'really like'
                    elif sentiment > 0:
                        verb = 'like'
                    elif sentiment < -1:
                        verb = "really don't like"
                    elif sentiment < 0:
                        verb = "don't like"
                    if verb:
                        # Echoing the user's response
                        response += '%s %s %s.' % (random.choice(
                            ['Ok, so you', 'You', 'So you', 'Ok, you']), verb, moviesString)
                        response += unkString
                    else:
                        # If there is a movie but the sentiment is 0
                        response += 'I am not quite sure how you feel about %s' % moviesString
                        # If no movies were found in the response, ask for
                        # clarification.

                    # The same, only for genres
                    for genre in self.userGenres():
                        if self.userGenres().count(genre) > 2 and not genre in self.recommendedGenres and not genre in userGenresOld:
                            response += random.choice([' Hmm, it seems you like %s movies!',
                                                       ' Oh, I see you like %s movies!',
                                                       ' Ok, based on your movie preferences it seems you like %s movies!']) % genre.lower()
                            self.recommendedGenres.append(genre)
                            break
                else:
                    response += self.askForClarification()

            # Now process genres
            if self.askAboutGenres:
                input = input.lower()
                userResponse = self.extractGeneres(input)
                genres, sentiment, sentimentWords = userResponse.things, userResponse.sentiment, userResponse.words
                if self.deixis and not genres:
                    genres = self.deixis

                if self.deixis and not genres:
                    genres = self.deixis
                if genres and not sentiment:
                    self.deixis = genres
                    response += "I am not sure what your opinion is about %s. Can you clarify?" % self.conjPhraseFromList(
                        genres, False)

                elif sentiment and not genres:
                    if (float(self.askAboutEmotion) / 5.0).is_integer():
                        response += self.askForClarification()
                    else:
                        response += self.respondToEmotion(
                            sentimentWords, sentiment)
                elif genres:
                    prev = []
                    indb = self.genres.intersection(genres)
                    for genre in indb:
                        if genre in self.userPrefs['genres'].keys():
                            prev.append(genre)
                        self.userPrefs['genres'][genre] = sentiment
                    unkString = ''
                    if indb != set(genres):
                        unks = [genre for genre in genres if not genre in indb]
                        unkString += ' Unfortunately, I do not have data about ' + self.conjPhraseFromList(unks) + ',\n'\
                            'so I will not be able to take them into account in my recommendation.'
                    # Create a string which represents the list of movies
                    if prev:
                        response += random.choice(['I am revising your opinion about %s. ',
                                                   'Gotcha, updating your listed rating of %s. ',
                                                   'Right, so you\'re giving me a new opinion on %s. '
                                                   ]) % self.conjPhraseFromList(prev, False)
                    if len(genres) > 1:
                        genresString = ", ".join(["\"%s\"" % genre for genre in genres[
                                                 :-1]]) + " and \"%s\"" % genres[-1]
                    else:
                        genresString = "\"%s\"" % genres[0]

                    # According to the sentiment, add a verb to the response
                    if sentiment > 0:
                        verb = 'like'
                    else:
                        verb = "don't like"

                    if verb:
                        response += 'Ok, you %s %s.' % (verb, genresString)
                    else:
                        response += 'I am not quite sure how you feel about %s' % genresString
                # If no movies were found in the response, ask for
                # clarification.
                else:
                    response += self.askForClarification()

            if self.firstTimeAskAboutGenres and self.getNumDataMovies() > 2:
                self.askAboutMovies = False
                self.askAboutGenres = True
                response += " Now tell me about some genres and what whether you like them."
                response += "\nBased on the movies you like, may I recommend the following genres: %s." % self.conjPhraseFromList(
                    list(set(self.userGenres())), False)

            elif self.firstTimeAskAboutGenres and verb:
                response += self.inquireFurther('movies')
            if self.getNumDataGenres() > 2:
                self.askAboutMovies = False
                self.askAboutGenres = False
                self.giveRecs = True
            elif (self.askAboutGenres and verb):
                if self.firstTimeAskAboutGenres:
                    self.firstTimeAskAboutGenres = False
                else:
                    response += self.inquireFurther('genres')
            if self.giveRecs:
                # This is where the recommendation is given
                vec = [0 for i in range(len(self.titles))]
                movPref = self.getDataMovies()
                genrePref = self.getDataGenres()
                usrmvDict = {}
                for i in range(len(self.titlesPlain)):
                    for movie in movPref:
                        if movie in self.titlesPlain[i]:
                            # gets the index of the movie and puts it in usrmvdict
                            usrmvDict[movie] = i
                movPrefUnChanged = self.getDataMovies()
                for movie in movPref:
                    vec[usrmvDict[movie]] = 1
                    vec[usrmvDict[movie]] = self.userPrefs['movies'][movie]
                response += " Based on the data you gave me, my recommendation to you is: " + str(self.recommend(usrmvDict, genrePref, vec))
            #input =  self.extractMovies(input)
            #response = self.extractGeneres(input)
            # I like "Avatar" "The Matrix" "Passengers"
            # I Like "Comedy" "Action" "Thriller"
            #input =  self.extractMovies(input)
            #response = self.extractGeneres(input)

        return response


    def userGenres(self):
        userGenres = []
        for movie in self.userPrefs['movies'].keys():
            if self.userPrefs['movies'][movie] > 0:
                for title in self.titles:
                    if movie in self.handleArticle(title[0]):
                        userGenres.extend(title[1].split('|'))
        return userGenres

    def getGenerePat(self):
        return '(' + '|'.join(self.genres) + ')'

    # Pattern for finding a movie and an optional year in double quotation
    # marks
    quatedMovieNamePatter = "\"([A-Za-z,\(\)!&.:\- '\d]+)( \(\d\d\d\d\))?\""

    splitWords = '(' + '|'.join(("and", "but", "yet",
                                 "though", ",", "\.", ";", "!")) + ')'

    def isolateMovieNames(self, line):
        #statements = re.split(self.splitWords.strip(),line)
        # for i in range(0,len(statements),2):
        #    statement =  statements[i]
        # Find all occurcenes of pairs (movie,year?) inside double quotation
        # marks
        moviesAndYear = [find for find in re.findall(
            self.quatedMovieNamePatter, line)]
        # (year is optional)
        movies = []
        warnings = []
        for movie in moviesAndYear:
            # For each movie, year pair:
            # Get the mapped name of the movie the user talks about
            title = self.titlesDict.get(movie[0])
            if title:
                # If this movie has a name in the database, append the official
                # name to the list of movies
                movies.append(title[:-7])
            else:  # Otherwise, just append the name of the movie. this will not be taken into account in the user's preferences
                movies.append(movie[0])
            if title and movie[1] and movie[1][-5:-1] != title[-5:-1]:
                # If a year was found in the user's response, and it is not the
                # correct year for this movie, then mention it.
                warnings.append("(Just saying, %s actually aired on %s. I am going to assume this is what you meant.) " % (
                    movie[0], title[-5:-1]))
        line = re.sub(self.quatedMovieNamePatter, '', line)
        return movies, line, warnings

    def isolateGenereNames(self, line):
        generes = [find[0] for find in re.findall(self.getGenerePat(), line)]
        line = re.sub(self.getGenerePat(), '', line)
        return generes, line

    def getSentiment(self, line):
        line = line.lower()
        line = line.split()
        sentimentScore = .0
        wss = []
        for word in line:
            negated = 'not_' in word
            if negated:
                word = word[4:]
            sentiment = self.sentiment.get(word)
            if not sentiment:
                sentiment = self.sentiment.get(word[:-1])
            if not sentiment:
                sentiment = self.sentiment.get(word[:-2])
            if sentiment:
                if sentiment == 'pos':
                    sentiment = 1.0
                elif sentiment == 'neg':
                    sentiment = -1.0
                if negated:
                    sentiment *= -1.0
                sentimentScore += sentiment
                wss.append((word, sentiment))
        if sentimentScore > 0:
            sentVal = 1
        elif sentimentScore < 0:
            sentVal = -1
        else:
            sentVal = None
        return sentimentScore, [ws[0] for ws in wss if ws[1] == sentVal]

    def extractMovies(self, input):
        movies, sentiments, warnings = self.isolateMovieNames(input)
        sentimentVals, sentimentWords = self.getSentiment(sentiments)
        return Response(movies, sentimentVals, sentimentWords), warnings

    def extractGeneres(self, input):
        geners, sentiments = self.isolateGenereNames(input)
        sentiments, sentimentWords = self.getSentiment(sentiments)
        return Response(geners, sentiments, sentimentWords)

    def transform(self, input):
        pass

    ##########################################################################
    # 3. Movie Recommendation helper functions                                  #
    ##########################################################################

    def inquireFurther(self, string):
        return random.choice([" Which other %s do you have an opinion about?",
                              " Tell me about some more %s please.",
                              " Please tell me about some other %s you watched.",
                              " Give me some more %s!"]) % string

    def conjPhraseFromList(self, lst, quotes=True):
        if quotes:
            qs = "\""
        else:
            qs = ''
        if len(lst) > 1:
            string = ", ".join(["%s%s%s" % (qs, movie, qs) for movie in lst[
                               :-1]]) + " and %s%s%s" % (qs, lst[-1], qs)
        else:
            string = "%s%s%s" % (qs, lst[0], qs)
        return string

    articles = "(l'|de|di|der|das|die|la|le|the|an|a|L'|De|Di|Der|Das|Die|La|Le|The|An|A)"

    def handleArticle(self, title):
        "Returns a set with all possible spelling variants of the title"
        # Get all expressions inside parantheses
        inParens = re.findall('( \(([^\(\)]+)\))', title)
        # Get all expressions that occur before a colon
        beforeColon = [find[1]
                       for find in re.findall('(^|\(|\) )([^\(\):]+)', title)]

        # All the expressions inside parens, and all the expressions before a
        # colon,
        titles = [title] + beforeColon + [find[1] for find in inParens]
        # are spelling variants

        newTitles = []
        for title in titles:
            # Now for each recognized title:
            # Find articles at the end of the title (of the form ", the")
            find = re.findall(", %s" % self.articles, title.lower())
            newTitles.append(title)  # Save unchanged basic title
            newTitles.append(title.lower())  # Save title with lowercase
            artsRemoved = re.sub('((^|\) )%s |, %s( \(|$))' % (
                self.articles, self.articles), '', title)  # Title with articles removed
            newTitles.append(artsRemoved)  # Save title with articles removed
            # Save title with articles removed and lower case
            newTitles.append(artsRemoved.lower())
            if find:
                # If there are final articles (of the form ", the"), move them
                # to the beginning and save the result (both capitalized and
                # lower)
                newTitles.append(find[0].capitalize() +
                                 ' ' + title[:-2 - len(find[0])])
                newTitles.append(find[0].lower() + ' ' +
                                 title[:-2 - len(find[0])])
            else:
                newTitles.append(title)
        return set(newTitles)

    def inDataBase(self, title):
        "Old. I think useless."
        return set(self.handleArticle(title)).intersection(self.titlesWithoutYear)

    def read_data(self):
        """Reads the ratings matrix from file"""
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        # A dictionary from spelling variant to actual movie title.
        self.titlesDict = {}
        # For example, this would map "The Matrix" and "Matrix, The" to the
        # same object
        self.titlesWithoutYear = set([])
        self.titlesWithYear = set([])
        self.titles, self.ratings = ratings()
        self.binarize()
        # Collect a list of all titles
        self.titlesPlain = [(title[0]) for title in self.titles]
        for title in self.titlesPlain:
            # For each title:
            # Get the set of all spelling variants using this method ([:-7]
            # ignores the year)
            handled = self.handleArticle(title[:-7])
            for variant in handled:
                # For each variant, add it to the titlesDict
                self.titlesDict[variant] = title
            self.titlesWithoutYear = self.titlesWithoutYear.union(
                handled)  # Keep track of all the existing titles
            # print self.titlesWithoutYear.union(handled)
            # print "\n\n"
            self.titlesWithYear = self.titlesWithYear.union(set(
                [(handledTitle, title[-5:-1]) for handledTitle in handled]))  # Keep track with years
        reader = csv.reader(open('data/sentiment.txt', 'rb'))
        self.sentiment = dict(reader)
        print self.titlesPlain


    def binarize(self):
        """Modifies the ratings matrix to make all of the ratings binary"""
        for movie in range(len(self.ratings)):
            for user in range(len(self.ratings[movie])):
                val = self.ratings[movie][user]
                if val == 0:
                    self.ratings[movie][user] = 0
                elif val < 2.5:
                    self.ratings[movie][user] = -1
                else:
                    self.ratings[movie][user] = 1

    def cosine_similarity(self,v1,v2):
        "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i]; y = v2[i]
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        return sumxy/math.sqrt(sumxx*sumyy)

    def cosine_measure(self, v1, v2):
        prod = self.dotProduct(v1, v2)
        len1 = math.sqrt(self.dotProduct(v1, v1))
        len2 = math.sqrt(self.dotProduct(v2, v2))
        return prod / (len1 * len2)

    def distance(self, u, v):
        """Calculates a given distance function between vectors u and v"""
        return self.cosine_similarity(u,v)
        if len(u) == len(v):
            sqrdsum = 0
            for i in range(len(u)):
                sqrdsum += (u[i] - v[i])**2
            return math.sqrt(sqrdsum)
        else:
            return None


    def dotProduct(self,u,v):
        if len(u) == len(v):
            dotproduct = 0
            for i in range(len(u)):
                dotproduct += u[i] * v[i]
            return dotproduct
        else:
            return Nones

    def second_largest(self,numbers):
        count = 0
        m1 = m2 = float('-inf')
        for x in numbers:
            count += 1
            if x > m2:
                if x >= m1:
                    m1, m2 = x, m1
                else:
                    m2 = x
        return m2 if count >= 2 else None

    def recommend(self, usrmvDict, usrGenres, u):
        """Generates a list of movies based on the input vector u using
        collaborative filtering
        u: is a vector of size len(self.titles) that is the users binarized ratings for all movies; 0 for unrated
        self.ratings[movies][user]: is all the movies (9125) and the ratings of all users (671)
        self.titles[movieIndex][1]: all the genres the film is in
        usrmvDict dict of movie to index of movie
        genrePref list of prefered genres
        vec = list of all movie preferences ordered by index location
        """
        rxi = []
        divisor = len(usrGenres)
        userMovies = self.getDataMovies()
        for movie in range(len(self.ratings)):
            val = 0
            mvGen = self.titles[movie][1]
            genSimCount = 0
            for genre in usrGenres:
                if genre in mvGen.lower():
                    genSimCount += 1
            for usrmv in usrmvDict.keys():
                index = usrmvDict[usrmv]
                #               s_{ij}
                val += self.distance(self.ratings[movie], self.ratings[index]) * math.log(10 + 10*genSimCount)
            rxi.append(val)
        index = rxi.index(max(rxi))
        mov = self.titles[index][0]
        while mov in userMovies:
            index = rxi.index(self.second_largest(rxi))
            mov = self.titles[index][0]
        return mov

    ##########################################################################
    # 4. Debug info                                                             #
    ##########################################################################

    def debug(self, input):
        """Returns debug information as a string for the input string from the REPL"""
        # Pass the debug information that you may think is important for your
        # evaluators
        # I like "Avatar" "The Matrix" "Passengers"
        # I Like "Comedy" "Action" "Thriller"
        debug_info = 'debug info'
        return debug_info

    ##########################################################################
    # 5. Write a description for your chatbot here!                             #
    ##########################################################################
    def intro(self):
        return """
      Charlie is a happy little chatbot that provides users with movie recommendations based on their opinion of a number of movies and genres.
      Users provide their opinion on at least 5 movies and 5 genres, and the chatbot applies the collaborative filtering method to find
      the movies they are most likely to enjoy based on the ratings of users from Netflix. Charlie can also provide some information about the movies in his database.
      """

    ##########################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    ##########################################################################

    def bot_name(self):
        return self.name

if __name__ == '__main__':
    Chatbot()
