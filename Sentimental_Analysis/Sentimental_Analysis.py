'''----------------------SENTIMENTAL ANALYSIS OF COVID-19 TWEETS - VISUALIZATION DASHBOARD------------------'''

'''---Importing Of Required Libraries and Modules---'''

'''Impoting Tweepy for Accessing Twitter API'''
import tweepy
from tweepy import StreamListener
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
'''Importing TextBlob For Analysing Sentiments'''
from textblob import TextBlob
'''Importing the JSON and CSV files'''
import json
import csv
'''Importing Regular Expression(RegEx) module for Cleaning the Tweets'''
import re
'''Importing Numpy and Pandas for processing the Collected Data'''
import numpy as np
import pandas as pd
'''Importing Matplotlib for the Visualization of data'''
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
'''Importing the File containing the required Keys and Access Tokens to access Twitter API'''
import Credentials1
'''Importing of all the required libraries has been over'''

class TwitterClients():
    
    
    def __init__(self,twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client=API(self.auth)
        self.twitter_user=twitter_user

    '''Method for getting the user info'''

    def get_twitter_client_api(self):
        return self.twitter_client

    '''Method for getting the tweets from the User's Timeline'''
     
    def get_user_timeline_tweets(self,num_tweets):
        tweets=[]
        for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
            tweets.append(tweet.text)
        return tweets

    '''Method to get the list of Friends of the user'''

    def get_friendlist(self,num_friends):
        friend_list=[]
        for tweet in Cursor(self.twitter_client.friends,id=self.twitter_user).items(num_friends):
            friend_list.append(tweet)
        return friend_list

    '''Method for acquiring the Home Timeline Tweets'''

    def get_home_timeline_tweets(self,num_tweets):
        home_timeline_tweets=[]
        for tweet in Cursor(self.twitter_client.home_timeline,id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet.text)
        return home_timeline_tweets



'''Class for Authenticating the User'''

class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth=tweepy.OAuthHandler(Credentials1.consumer_key,Credentials1.consumer_secret)
        auth.set_access_token(Credentials1.access_token,Credentials1.access_token_secret)
        return auth


'''Class for Streaming the Real Time filtered Tweets from Twitter '''
class TwitterStreamer():

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self,fetched_tweets_filename,hashtag_list):

        listener = TwitterListener(fetched_tweets_filename)
        auth=self.twitter_authenticator.authenticate_twitter_app()
        stream=Stream(auth,listener)
        stream.filter(track=hashtag_list)


        
class TwitterListener(StreamListener):

    def __init__(self,fetched_tweets_filename):
        self.fetched_tweets_filename=fetched_tweets_filename


    def on_data(self,data):
        auth=tweepy.OAuthHandler(Credentials1.consumer_key,Credentials1.consumer_secret)
        auth.set_access_token(Credentials1.access_token,Credentials1.access_token_secret)
        api=tweepy.API(auth)
        for tweet in tweepy.Cursor(api.search,q="corona",count=100,lang="en",since="2020-07-13").items():
            with open('Sent1.csv','a',encoding='utf-8') as f:
                print(tweet.created_at,tweet.text)
                csvWriter=csv.writer(f)
                csvWriter.writerow([tweet.created_at,tweet.text])

    def on_error(self,status):
        if status == 420:
            return False
        print(status)


class TweetsAnalyser():

    '''Method to clean and preprocess the collected Tweets'''
    
    def clean_tweets(self,tweet):
        tweet=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
        return tweet

    '''Method to Analyse the Sentiment of tweets using TextBlob'''

    def analyze_sentiment(self,tweet):
        analysis=TextBlob(self.clean_tweets(tweet))
        positive=0

        if analysis.sentiment.polarity>0:
            return 1
        elif analysis.sentiment.polarity<0:
            return -1
        else:
            return 0

    '''Method to process the collected preprocessed data to create a DataFrame'''
   

    def  tweets_to_dataframe(self,tweets):
        df=pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Sentiments'])
        Corona=[]
        for tweet in df['Sentiments']:
            if 'COVID-19'or 'Corona' or '#corona' in tweet:
                Corona.append(tweet)
        df['Corona']=np.array([tweet for tweet in Corona])
        df['id']=np.array([tweet.id for tweet in tweets])
        df['len']=np.array([len(tweet.text) for tweet in tweets])
        df['date']=np.array([tweet.created_at for tweet in tweets])
        df['source']=np.array([tweet.source for tweet in tweets])
        df['likes']=np.array([tweet.favorite_count for tweet in tweets])
        df['retweets']=np.array([tweet.retweet_count for tweet in tweets])
        return df




if __name__ == "__main__":

    print("-----------------------------------Tweet Analyser----------------------------------------------")
    cont=1
    while cont==1:
        print("\n\n1.Real Time Streaming of Tweets\n2.Getting the home line tweets of the Person/Organization \n3.Analysing the Tweets handling by a Person/Organization\n4.Sentimental Analysis of the COVID-19 Tweets\n")
        choice=int(input("Enter Your Choice: "))
        if choice==1:
            hashtag_list=['COVID-19','corona virus','novel corona','pandemic']
            fetched_tweets_filename="tweets.json"
            twitter_streamer=TwitterStreamer()
            twitter_streamer.stream_tweets(fetched_tweets_filename,hashtag_list)

        elif choice==2:
            person=str(input("Enter the person: "))
            num=int(input("Enter number of Tweets: "))
            twitter_client=TwitterClients(person)
            print(twitter_client.get_home_timeline_tweets(num))


        elif choice==3:
            person=str(input("Enter the person: "))
            num=int(input("Enter number of Tweets: "))
            twitter_client=TwitterClients()
            api=twitter_client.get_twitter_client_api()
            tweets=api.user_timeline(screen_name=person,count=num) 
            tweet_analyzer=TweetsAnalyser()
            df=tweet_analyzer.tweets_to_dataframe(tweets)
            contin=1
            while contin ==1:
                print("1.Average Number of Words in Tweets\n2.Maximum number of Likes\n3.Maximum Number of Retweets\n4.Analysis of Likes\n5.Analysis of Retweets\n6.Analysis of Sentiment")
                option=int(input("Enter Your option: "))
                if option ==1:
                    print(np.mean(df['len']))

                elif option == 2:
                    print(np.max(df['likes']))

                elif option == 3:
                    print(np.max(df['retweets']))

                elif option == 4:
                    time_likes=pd.Series(data=df['likes'].values, index=df['date'])
                    time_likes.plot(figsize=(16,4),color='g',label='Likes',legend=True)
                    plt.show()

                elif option == 5:
                    time_retweets=pd.Series(data=df['retweets'].values, index=df['date'])
                    time_retweets.plot(figsize=(16,4),color='g',label='Retweets',legend=True)
                    plt.show()

                else:
                    df['Analysis']=np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['Corona']])
                    sentiment= pd.Series(df['Analysis'].values,index=df['date'])
                    sentiment.plot(figsize=(18,6),color='g')
                    plt.show()
                contin=int(input("Enter what next: "))

        else:
            auth=tweepy.OAuthHandler(Credentials1.consumer_key,Credentials1.consumer_secret)
            auth.set_access_token(Credentials1.access_token,Credentials1.access_token_secret)
            api=tweepy.API(auth)
            with open('Sent1.csv','r',encoding='utf-8-sig') as f:
                df=pd.read_csv(f)
                a=[]
                for tweet in df['Tweets']:
                    analysis=TextBlob(str(tweet))
                    a.append(analysis.sentiment.polarity)
            df['Analysis']=np.array(a)
            sentiment= pd.Series(df['Analysis'].values,index=df['Dates'])
            sentiment.plot(figsize=(18,6),color='g')
            plt.show()

        cont=int(input("Do you want to Continue?: "))
    
