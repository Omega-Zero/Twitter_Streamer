from tweepy import API
from tweepy import Cursor

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import credentials
import numpy as np
import pandas as pd
import json


class TwitterClient():
    #call authenticate methods and gather data for a given user
    #if default none argument is passed for user, methods will return authenticated account's data
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user


    def get_twitter_client_api(self):
        return self.twitter_client
        
    #returns a given number of a given user's tweets
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    #returns the friends list of a given user
    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    #returns 
    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twiter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

            

class TwitterAuthenticator():
    """
    Establishes credentials to authenticate api connection for use in any method/func with credentials from seperate file
    Make sure your credential file is in same folder as this file and is named "credentials.py" or it will throw a ModuleNotFoundError: No module named 'credentials' or similar
    """
    def authenticate_twitter_app(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterStreamer():
    """
    Class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    #takes in a .txt with all the fetched tweets and hashtag array list
    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        listener = TwitterFormmatedListener(fetched_tweets_filename)
        #calls credentials              
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        
        #returns tweets with keywords in a given array
        stream.filter(track = hash_tag_list)



class StdOutListener(StreamListener):
    """
    basic listener that prints resieved tweets to stdout
    """
    #overwritten method that takes in the data from listener
    def on_data(self, data):
        print("THIS IS A NEW TWEET-------------- \n" , data)
        print(data)

    #error catcher that prints error or kicks you out based on error thrown
    def on_error(self, status):
        #twitter has rate limits to kick misused bots. if 420 error is thrown, kill everything with negativity
        if status == 420:
            return False
        print(status)


class TwitterListener(StreamListener):
    """
    listener that prints recieved tweets to given file and prints live json;
    """
    def __init__ (self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
        
    #overwritten method that takes in the data from listener
    def on_data(self, data):
        print("THIS IS A NEW TWEET-------------- \n" , data)
        #if something in the incoming data isnt right, throw error
        try:
           
            print("data: \n")
            print(data)
            #writes to given filename
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    #error catcher that prints error or kicks you out based on error thrown
    def on_error(self, status):
        #twitter has rate limits to kick misused bots. if 420 error is thrown, kill everything with negativity
        if status == 420:
            return False
        print(status)



class TwitterFormmatedListener(StreamListener):
    """
    listener that prints recieved tweets to given file and prints live json;
    """
    def __init__ (self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
        
    #overwritten method that takes in the data from listener
    def on_data(self, data):
        print("------------------------------THIS IS A NEW TWEET-------------------------------------------------\n")
        tweet_array = " "
        
        #if something in the incoming data isnt right, throw error
        #this is where we would otherwise send data to the SQL DB instead of print/file
        try:
            
            user_id = json.loads(data)['id']
            tweet_array = tweet_array + "user_id: " + str(user_id)  + " | "
            
           # user = api.get_user(user_id)
           # print(user.screen_name)

            created_at = json.loads(data)['created_at']
            tweet_array = tweet_array + "created_at: " + str(created_at)  + " | "

            tweet_text = json.loads(data)['text']
            tweet_array = tweet_array + "TWEET_TEXT: " + tweet_text + " | "
            

            #writes to given filename
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write("|| ---------------------------------------------NEW TWEET DATA ------------------------------------------------------------- || \n")
                tf.write(tweet_array)
                tf.write("\n\n-------JSON -------\n")
                tf.write(data)
            #prints json block
            print ("Array: " , tweet_array)
            print("\nJSON data:>>>>>> \n")
            print(data)
            
        except BaseException as e:
            print("\n Error on_data: %s" % str(e))
            print("\n \n \n")
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write("\n ERROR")
                tf.write(str(e))
                tf.write("\n")
        return True

    #error catcher that prints error or kicks you out based on error thrown
    def on_error(self, status):
        #twitter has rate limits to kick misused bots. if 420 error is thrown, kill everything with negativity
        if status == 420:
            return False
        print(status)



class TweetAnalyzer():
    """
    Functionality for analyzing/categorizing content from tweets
    """
    def tweets_to_data_frame(self, tweets):
        #loop through list of tweets and extract tweet text
        df =pd.DataFrame(data=[tweet.text for tweet in tweets], columns =['Tweets'])
        return df
    


if __name__ == "__main__":

    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()

   # tweets = api.user_timeline(screen_name="POTUS", count=20)
   # print(tweets)

    #list of keywords for stream to find
    keyword_list = ["DOGE", "Stonk", "GME"]
    fetched_tweets_filename = "tweets.json"

   # twitter_client = TwitterClient()
    #print(twitter_client.get_user_timeline_tweets(1))

  #  create the streamer object and call its method 
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(fetched_tweets_filename, keyword_list)
    
                    
