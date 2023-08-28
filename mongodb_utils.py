
from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://127.0.0.1:27017/")

mydb = client['academicworld']

publication_db = mydb.publications
faculty_db = mydb.faculty

def get_topKeywordsByYear(yearinput):
    year = 2022 - yearinput
    
    pipline = [{"$project": {"year":1, "keywords":1}},
               { "$match" : { "year": { "$gte" : year }}},
               { "$unwind" : "$keywords" },
               { "$group" : { "_id":"$keywords.name" , "score_sum" :{ "$sum" : "$keywords.score" }}},
               { "$sort" : {"score_sum": -1}},
               { "$limit" : 15 }
    ]
               
    data = pd.DataFrame(list(publication_db.aggregate(pipline)))
    data.rename(columns={"_id": "keyword_name", "score_sum": "score_sum"}, inplace=True)
    return data

def get_topUniversity(keyword1, keyword2 = None):
    pipline = [
        {
            "$unwind" : "$keywords"
        },
        {
            "$match" :{"$or": [{"keywords.name" : keyword1}, {"keywords.name" : keyword2}]} 
        },
        {
            "$group" : {"_id": "$affiliation.name", "score_sum" : {"$sum" : "$keywords.score" }}
        },
        {
            "$sort": {"score_sum" : -1}
        },
        { "$limit" : 10 }
    ]
         
    data =  pd.DataFrame(list(faculty_db.aggregate(pipline)))
    data.score_sum = data.score_sum.round(2)
    data.rename(columns={"_id": "University", "score_sum": "score_sum"}, inplace=True)

    return data





