from mongo_utils import get_database, convert_to_dataframe, save_to_csv
import pandas as pd

def analyze_users():
    db = get_database()
    
    # 1. Usuarios más activos (posts + comentarios)
    pipeline = [
        {
            "$lookup": {
                "from": "posts",
                "localField": "_id",
                "foreignField": "author_id",
                "as": "user_posts"
            }
        },
        {
            "$lookup": {
                "from": "posts",
                "localField": "_id",
                "foreignField": "comments.author_id",
                "as": "user_comments"
            }
        },
        {
            "$project": {
                "username": 1,
                "subscriptions": 1,
                "post_count": { "$size": "$user_posts" },
                "comment_count": { "$size": "$user_comments" },
                "total_activity": {
                    "$add": [
                        { "$size": "$user_posts" },
                        { "$size": "$user_comments" }
                    ]
                }
            }
        },
        {
            "$sort": { "total_activity": -1 }
        }
    ]
    
    results = db.users.aggregate(pipeline)
    df = convert_to_dataframe(results)
    save_to_csv(df, "user_activity.csv")
    
    # 2. Análisis de suscripciones
    pipeline = [
        {
            "$group": {
                "_id": "$subscriptions",
                "count": { "$sum": 1 },
                "avg_friends": { "$avg": { "$size": "$friends" } }
            }
        }
    ]
    
    results = db.users.aggregate(pipeline)
    df = convert_to_dataframe(results)
    save_to_csv(df, "subscription_analysis.csv")
    
    print("Análisis de usuarios completado!")

if __name__ == "__main__":
    analyze_users() 