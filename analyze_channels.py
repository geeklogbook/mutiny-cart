from mongo_utils import get_database, convert_to_dataframe, save_to_csv
import pandas as pd

def analyze_channels():
    db = get_database()
    
    # 1. Canales más populares
    pipeline = [
        {
            "$lookup": {
                "from": "posts",
                "localField": "_id",
                "foreignField": "channel_id",
                "as": "channel_posts"
            }
        },
        {
            "$project": {
                "name": 1,
                "description": 1,
                "member_count": { "$size": "$members" },
                "post_count": { "$size": "$channel_posts" },
                "avg_comments_per_post": {
                    "$avg": {
                        "$map": {
                            "input": "$channel_posts",
                            "as": "post",
                            "in": { "$size": "$$post.comments" }
                        }
                    }
                }
            }
        },
        {
            "$sort": { "post_count": -1 }
        }
    ]
    
    results = db.channels.aggregate(pipeline)
    df = convert_to_dataframe(results)
    save_to_csv(df, "channel_popularity.csv")
    
    # 2. Análisis de actividad por canal
    pipeline = [
        {
            "$lookup": {
                "from": "posts",
                "localField": "_id",
                "foreignField": "channel_id",
                "as": "posts"
            }
        },
        {
            "$unwind": "$posts"
        },
        {
            "$group": {
                "_id": "$name",
                "total_comments": {
                    "$sum": { "$size": "$posts.comments" }
                },
                "unique_authors": {
                    "$addToSet": "$posts.author_id"
                }
            }
        },
        {
            "$project": {
                "channel_name": "$_id",
                "total_comments": 1,
                "unique_author_count": { "$size": "$unique_authors" }
            }
        }
    ]
    
    results = db.channels.aggregate(pipeline)
    df = convert_to_dataframe(results)
    save_to_csv(df, "channel_activity.csv")
    
    print("Análisis de canales completado!")

if __name__ == "__main__":
    analyze_channels() 