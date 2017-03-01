
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


# TODOs:
# I like 'a' 'b' and 'c' returns {"a' 'b' and 'c": 1.0}
# Add NOT_ after negatd words


class Response:

    def __init__(self, things, sentiment):
        self.things = things
        self.sentiment = sentiment


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    punc = [",", "!", ".", ";", "?", "but", "yet"]
    negationWords = ['not', 'nor', "n't", "didn't",
                     "wasn't", "don't", "dont", "didnt", "wasnt"]

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

        self.askAboutMovies = True
        self.askAboutGenres = False
        self.giveRecs = False
        self.firstTimeAskAboutGenres = True

    def askForClarification(self): return random.choice(["Sorry, I didn't get that. Can you say it again?",
                                                         "Sorry, I missed that. Can you say it differently?",
                                                         "I am sorry, but I'm not sure what you meant. Please say it again."])

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

        if self.is_turbo == True:
            response = 'processed %s in creative mode!!' % input
        else:

            dont = None  # Whether the sentiment is positive or negative

            if self.askAboutMovies:
                userResponse = self.extractMovies(input)
                movies, sentiment = userResponse.things, userResponse.sentiment
                # If the bot found any movies, it will add to the response the
                # echo of those movies:

                if movies and not sentiment:
                    response += "I am not sure what your opinion is about %s. Can you clarify?" % self.conjPhraseFromList(
                        movies)
                elif movies:
                    indb = self.titlesWithoutYear.intersection(movies)
                    for movie in indb:
                        self.userPrefs['movies'][movie] = sentiment
                    unkString = ''
                    if indb != set(movies):
                        unks = [movie for movie in movies if not movie in indb]
                        unkString += ' Unfortunately, I do not have data about ' + self.conjPhraseFromList(unks) + ',\n'\
                            'so I will not be able to take them into account in my reccomendations.'
                    # Create a string which represents the list of movies
                    if len(movies) > 1:
                        moviesString = ", ".join(["\"%s\"" % movie for movie in movies[
                                                 :-1]]) + " and \"%s\"" % movies[-1]
                    else:
                        moviesString = "\"%s\"" % movies[0]

                    # According to the sentiment, add a verb to the response
                    if sentiment > 0:
                        dont = 'like'
                    else:
                        dont = "don't like"
                    if dont:
                        response += '%s %s %s.' % (random.choice(
                            ['Ok, so you', 'You', 'So you', 'Ok, you']), dont, moviesString)
                        response += unkString
                    else:
                        response += 'I am not quite sure how you feel about %s' % moviesString
                        # If no movies were found in the response, ask for
                        # clarification.
                else:
                    response += self.askForClarification()

            if self.askAboutGenres:
                input = input.lower()
                userResponse = self.extractGeneres(input)
                genres, sentiment = userResponse.things, userResponse.sentiment

                if genres and not sentiment:
                    response += "I am not sure what your opinion is about %s. Can you clarify?" % self.conjPhraseFromList(
                        genres, False)

                elif genres:

                    indb = self.genres.intersection(genres)
                    for genre in indb:
                        self.userPrefs['genres'][genre] = sentiment
                    unkString = ''
                    if indb != set(genres):
                        unks = [genre for genre in genres if not genre in indb]
                        unkString += ' Unfortunately, I do not have data about ' + self.conjPhraseFromList(unks) + ',\n'\
                            'so I will not be able to take them into account in my reccomendations.'
                    # Create a string which represents the list of movies
                    if len(genres) > 1:
                        genresString = ", ".join(["\"%s\"" % genre for genre in genres[
                                                 :-1]]) + " and \"%s\"" % genres[-1]
                    else:
                        genresString = "\"%s\"" % genres[0]

                    # According to the sentiment, add a verb to the response
                    if sentiment > 0:
                        dont = 'like'
                    else:
                        dont = "don't like"

                    if dont:
                        response += 'Ok, you %s %s.' % (dont, genresString)
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

            elif self.firstTimeAskAboutGenres and dont:
                response += self.inquireFurther('movies')
            if self.getNumDataGenres() > 2:
                self.askAboutMovies = False
                self.askAboutGenres = False
                self.giveRecs = True
            elif (self.askAboutGenres and dont):
                if self.firstTimeAskAboutGenres:
                    self.firstTimeAskAboutGenres = False
                else:
                    response += self.inquireFurther('genres')
            if self.giveRecs:
                vec = [0 for i in range(len(self.titles))]
                movPref = self.getDataMovies()
                genrePref = self.getDataGenres()
                usrmvDict = {}
                for i in range(len(self.orgedTitlesWithoutYear)):
                    for movie in movPref:
                        if movie in self.orgedTitlesWithoutYear[i]:
                            usrmvDict[movie] = i
                for movie in movPref:
                    vec[usrmvDict[movie]] = self.userPrefs['movies'][movie]
                response += " Based on the data you gave me, my recommendation to you is:" + str(self.recommend(usrmvDict, genrePref, vec))
            #input =  self.extractMovies(input)
            #response = self.extractGeneres(input)
            # I like "Avatar" "The Matrix" "Passengers"
            # I Like "Comedy" "Action" "Thriller"

        return response

    def getGenerePat(self):
        return '(' + '|'.join(self.genres) + ')'

    quatedMovieNamePatter = "\"([A-Za-z '\d]+)\""

    splitWords = '(' + '|'.join(("and", "but", "yet",
                                 "though", ",", "\.", ";", "!")) + ')'

    def isolateMovieNames(self, line):
        #statements = re.split(self.splitWords.strip(),line)
        # for i in range(0,len(statements),2):
        #    statement =  statements[i]
        movies = [find for find in re.findall(
            self.quatedMovieNamePatter, line)]
        line = re.sub(self.quatedMovieNamePatter, '', line)
        return movies, line

    def isolateGenereNames(self, line):
        generes = [find[0] for find in re.findall(self.getGenerePat(), line)]
        line = re.sub(self.getGenerePat(), '', line)
        return generes, line

    def getSentiment(self, line):
        line = line.lower()
        line = line.split()
        sentimentScore = .0
        for word in line:
            negated = 'not_' in word
            if negated:
                word = word[4:]
            sentiment = self.sentiment.get(word)
            if sentiment:
                if sentiment == 'pos':
                    sentiment = 1.0
                elif sentiment == 'neg':
                    sentiment = -1.0
                if negated:
                    sentiment *= -1.0
                sentimentScore += sentiment
        return sentimentScore

    def extractMovies(self, input):
        movies, sentiments = self.isolateMovieNames(input)
        sentiments = self.getSentiment(sentiments)
        return Response(movies, sentiments)

    def extractGeneres(self, input):
        geners, sentiments = self.isolateGenereNames(input)
        sentiments = self.getSentiment(sentiments)
        return Response(geners, sentiments)

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
        if len(lst) > 1:
            if quotes:
                qs = "\""
            else:
                qs = ''
            string = ", ".join(["%s%s%s" % (qs, movie, qs)
                                for movie in lst[:-1]]) + " and \"%s\"" % lst[-1]
        else:
            string = "\"%s\"" % lst[0]
        return string

    articles = ('the', 'a', 'an')

    def handleArticle(self, title):
        toPrint = False
        if False and 'Germania anno zero' in title:
            toPrint = True
            print title
        inParens = re.findall('( \(([^\(\)]+)\))', title)
        titles = []
        if inParens:
            sub = 0
            for i in range(len(inParens)):
                titles.append(inParens[i][1])
                sub += len(inParens[i][0])
            titles.append(title[:-sub])
        else:
            titles.append(title)
        newTitles = []
        for title in titles:
            find = re.findall(
                ", (l'|de|di|der|das|die|la|le|the|an|a)", title.lower())
            if find:
                newTitles.append(find[0].capitalize() +
                                 ' ' + title[:-2 - len(find[0])])
            else:
                newTitles.append(title)
        if toPrint:
            print inParens
            print newTitles
        return set(newTitles)

    def inDataBase(self, title):
        return set(self.handleArticle(title)).intersection(self.titlesWithoutYear)
    'Sound and Fury'

    def read_data(self):
        """Reads the ratings matrix from file"""
        # This matrix has the following shape: num_movies x num_users
        # The values stored in each row i and column j is the rating for
        # movie i by user j
        self.titlesWithoutYear = set([])
        self.orgedTitlesWithoutYear = []
        self.titles, self.ratings = ratings()
        self.binarize()
        self.titlesPlain = [(title[0]) for title in self.titles]
        for title in self.titlesPlain:
            self.orgedTitlesWithoutYear.append(list(self.handleArticle(title[:-7]))[0])
            self.titlesWithoutYear = self.titlesWithoutYear.union(
                self.handleArticle(title[:-7]))
            # if len(self.handleArticle(title[:-7]))>1: print
            # self.handleArticle(title[:-7])
        reader = csv.reader(open('data/sentiment.txt', 'rb'))
        self.sentiment = dict(reader)

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

    def distance(self, u, v):
        """Calculates a given distance function between vectors u and v"""
        if len(u) == len(v):
            sqrdsum = 0
            for i in range(len(u)):
                sqrdsum += (u[i] - v[i])**2
            return math.sqrt(sqrdsum)
        else:
            return None

    def dotProduct(u,v):
        if len(u) == len(v):
            dotproduct = 0
            for i in range(len(u)):
                dotproduct += u[i] * v[i]
            return dotproduct
        else:
            return Nones

    def recommend(self, usrmvDict, usrGenres, u):
        """Generates a list of movies based on the input vector u using
        collaborative filtering
        u: is a vector of size len(self.titles) that is the users binarized ratings for all movies; 0 for unrated
        self.ratings[movies][user]: is all the movies (9125) and the ratings of all users (671)
        self.titles[movieIndex][1]: all the genres the film is in
        """
        rxi = []
        divisor = len(usrGenres)
        userMovies = self.getDataMovies()
        for movie in range(len(self.ratings)):
            val = 0
            mvGen = self.titles[movie][1]
            genSimCount = 0
            for genre in usrGenres:
                if genre in mvGen:
                    genSimCount += 1
            for usrmv in usrmvDict.keys():
                index = usrmvDict[usrmv]
                #               s_{ij}
                val += self.distance(self.ratings[movie], self.ratings[index]) * math.log(10 + 10*genSimCount)
            rxi.append(val)
        index = rxi.index(max(rxi))
        return self.orgedTitlesWithoutYear[index]

    ##########################################################################
    # 4. Debug info                                                             #
    ##########################################################################

    def debug(self, input):
        """Returns debug information as a string for the input string from the REPL"""
        # Pass the debug information that you may think is important for your
        # evaluators
        # I like "Avatar" "The Matrix" "Passengers"
        # I Like "Comedy" "Action" "Thriller"
        # len(movies.txt) = 9125 (index 9124)
        debug_info = 'debug info'
        return debug_info

    ##########################################################################
    # 5. Write a description for your chatbot here!                             #
    ##########################################################################
    def intro(self):
        return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
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
