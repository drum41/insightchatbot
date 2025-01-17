import pandas as pd
import pandas as pd
import random
import math
from typing import Dict, Any
def format_social_listening_data(df):
    # Interaction columns mapping
    interaction_columns = {
        'Reactions': ['Likes', 'Like', 'Reactions', 'Reaction', 'likes', 'like', 'reactions', 'reaction'],
        'Shares':   ['Shares', 'Share', 'shares', 'share'],
        'Comments': ['Comments', 'Comment', 'comments', 'comment'],
        'Views':    ['Views', 'View', 'views', 'view']
    }
    
    # Rename columns if they match any in interaction_columns
    interaction_found = False
    for standard_col, variations in interaction_columns.items():
        for variation in variations:
            if variation in df.columns:
                df.rename(columns={variation: standard_col}, inplace=True)
                interaction_found = True  # Mark that at least one interaction column exists
    
    # Create ChannelDeep column without removing or renaming 'Type'
    def generate_channel_deep(row):
        """
        Convert row['Type'] into a 'ChannelDeep' value without altering 'Type' itself.
        """
        channel_deep = row['Type']
        # Remove the words 'Topic' and 'Comment'
        channel_deep = channel_deep.replace('Topic', '').replace('Comment', '')
        # Capitalize the result
        channel_deep = channel_deep.capitalize()
        
        # If 'fb' is in the result, we assume it's Facebook
        if 'fb' in channel_deep.lower():
            channel_deep = 'Facebook '
        
        # If the Channel is 'fanpage', we override ChannelDeep to 'Fanpage'
        if row['Channel'].lower() == 'fanpage':
            channel_deep = 'Fanpage'
        
        return channel_deep.strip()
    
    df['ChannelDeep'] = df.apply(generate_channel_deep, axis=1)

    # Format PublishedDate to FormattedDate
    if 'PublishedDate' in df.columns:
        df['FormattedDate'] = pd.to_datetime(df['PublishedDate'], errors='coerce').dt.date

    # Example detection if 'Labels1' is found
    labels1_coverage = False
    if 'Labels1' in df.columns:
        total_ids = df['Id'].notnull().count()
        labels1_count = df['Labels1'].notnull().sum()

        # Calculate required sample size
        confidence_level = 99  # Confidence level in percentage
        margin_of_error = 0.03  # Margin of error in decimal

        Z = 2.576  # Z-score for 99% confidence level
        p = 0.5  # Proportion (use 0.5 for maximum variability)
        e = margin_of_error

        required_sample_size = math.ceil((Z**2 * p * (1 - p)) / (e**2))

        # Check if Labels1 meets or exceeds required sample size
        if labels1_count >= required_sample_size:
            labels1_coverage = True

    # Clean 'Content' and 'Title' columns
    def remove_special_chars(text):
        if not isinstance(text, str):  # Handle non-string values
            return text
        # Define the characters to remove
        special_chars = "{}()[]\\\":,/'|=;"
        return text.translate(str.maketrans("", "", special_chars))

    if 'Title' in df.columns:
        df['Title'] = df['Title'].apply(remove_special_chars)
    if 'Content' in df.columns:
        df['Content'] = df['Content'].apply(remove_special_chars)

    # Return the DataFrame plus any flags
    return df, interaction_found, labels1_coverage



def generate_brand_health_overview(
    df,
    params,
    brand_col: str = "Topic",
    date_col: str = "FormattedDate",
    channel_col: str = "ChannelDeep",
    sentiment_col: str = "Sentiment",
    type_col: str = "Type",
    reactions_col: str = "Reactions",
    shares_col: str = "Shares",
    comments_col: str = "Comments",
    views_col: str = "Views"
) -> dict:

    # Prepare the final output structure
    output = {"Topics": []}

    # Identify all unique brands in the dataset
    brands = df[brand_col].dropna().unique().tolist()

    for b in brands:
        # Filter DataFrame for this brand
        brand_df = df[df[brand_col] == b].copy()
        if brand_df.empty:
            continue

        # 1) Sentiment Percentages
        total_rows = len(brand_df)
        if total_rows == 0:
            pos_pct = neu_pct = neg_pct = 0.0
        else:
            pos_count = len(brand_df[brand_df[sentiment_col] == "Positive"])
            neu_count = len(brand_df[brand_df[sentiment_col] == "Neutral"])
            neg_count = len(brand_df[brand_df[sentiment_col] == "Negative"])

            pos_pct = 100.0 * pos_count / total_rows
            neu_pct = 100.0 * neu_count / total_rows
            neg_pct = 100.0 * neg_count / total_rows

        sentiment_dict = {
            "Positive": round(pos_pct, 2),
            "Neutral":  round(neu_pct, 2),
            "Negative": round(neg_pct, 2)
        }

        # 2) Mentions By Date
        # We'll group by date and count rows
        mentions_by_date = (
            brand_df
            .groupby(date_col, dropna=False)
            .size()
            .reset_index(name="Mention")
        )
        mentions_by_date_arr = []
        for _, row in mentions_by_date.iterrows():
            date_str = str(row[date_col]) if pd.notnull(row[date_col]) else ""
            mention_count = int(row["Mention"])
            mentions_by_date_arr.append({
                "Date": date_str,
                "Mention": mention_count
            })

        # 3) Mentions By Channel
        # Group by channel to count rows
        mentions_by_channel = (
            brand_df
            .groupby(channel_col, dropna=False)
            .size()
            .reset_index(name="Mention")
        )
        mentions_by_channel_arr = []
        for _, row in mentions_by_channel.iterrows():
            ch_value = row[channel_col]
            if pd.isna(ch_value):
                ch_value = "UnknownChannel"
            mentions_by_channel_arr.append({
                "ChannelDeep": str(ch_value),
                "Mention": int(row["Mention"])
            })

        # 4) SocialPostOverview
        #   - Filter out rows where type contains "news"
        #   - Count how many posts => rows where Type contains "Topic"
        #   - Count how many comments => rows where Type contains "Comment"
        #   - Ratio => comments / posts (avoid dividing by zero)
        non_news_df = brand_df[~brand_df[type_col].str.contains("news", case=False, na=False)].copy()

        # Number of posts -> rows where Type contains "Topic"
        number_of_posts = len(non_news_df[non_news_df[type_col].str.contains("Topic", case=False, na=False)])
        # Number of comments -> rows where Type contains "Comment"
        number_of_comments = len(non_news_df[non_news_df[type_col].str.contains("Comment", case=False, na=False)])

        if number_of_posts > 0:
            comment_post_ratio = number_of_comments / number_of_posts
        else:
            comment_post_ratio = 0.0

        social_post_overview_arr = [{
            "NumberofPost": number_of_posts,
            "NumberofComment": number_of_comments,
            "CommentPostRatio": round(comment_post_ratio, 2)
        }]

        # 5) Engagement
        # We'll sum Reactions, Shares, Comments, Views => total_engagement
        # Then compute rates per 'NumberofPost' (the non-news "Topic" count).
        # List of columns to process
        columns_to_clean = ['reactions_col', 'shares_col', 'comments_col', 'views_col']
        
        # Convert each column to numeric, coercing errors to NaN
        for col in columns_to_clean:
            brand_df[col] = pd.to_numeric(brand_df[col], errors='coerce')
            
        total_reactions = brand_df[reactions_col].sum(skipna=True)
        total_shares    = brand_df[shares_col].sum(skipna=True)
        total_comments  = brand_df[comments_col].sum(skipna=True)
        total_views     = brand_df[views_col].sum(skipna=True)

        total_engagement = total_reactions + total_shares + total_comments + total_views

        if number_of_posts > 0:
            reactions_rate  = total_reactions / number_of_posts
            comments_rate   = total_comments  / number_of_posts
            shares_rate     = total_shares    / number_of_posts
            views_rate      = total_views     / number_of_posts
            engagement_rate = total_engagement / number_of_posts
        else:
            reactions_rate  = 0.0
            comments_rate   = 0.0
            shares_rate     = 0.0
            views_rate      = 0.0
            engagement_rate = 0.0

        engagement_arr = [{
            "NumberofPost": number_of_posts,
            "Reactions": int(total_reactions),
            "ReactionsRate": round(reactions_rate, 2),
            "Comments": int(total_comments),
            "CommentsRate": round(comments_rate, 2),
            "Shares": int(total_shares),
            "SharesRate": round(shares_rate, 2),
            "Views": int(total_views),
            "ViewsRate": round(views_rate, 2),
            "Engagement": int(total_engagement),
            "EngagementRate": round(engagement_rate, 2),
        }]

        # Build the final object for this brand
        brand_obj = {
            "Topic": str(b),
            "Sentiment": sentiment_dict,
            "MentionsByDate": mentions_by_date_arr,
            "MentionsByChannel": mentions_by_channel_arr,
            "SocialPostOverview": social_post_overview_arr,
            "Engagement": engagement_arr
        }

        # Append to output["Topics"]
        output["Topics"].append(brand_obj)

    return output

#########################################################

def generate_top_post_details(
    df,
    params,
    topic_col: str = "Topic",
    id_col: str = "Id",
    url_col: str = "UrlTopic",
    title_col: str = "Title",
    date_col: str = "FormattedDate",
    content_col: str = "Content",
    reactions_col: str = "Reactions",
    comments_col: str = "Comments",
    shares_col: str = "Shares",
    views_col: str = "Views",
    top_n: int = 20,
    max_comments: int = 30,
) -> list:
    """
    Returns a list of dictionaries.
    Each dictionary has the structure:
    {
      "Topic": <str>,
      "TopPost": [
          {
              "UrlTopic": <str>,
              "Title": <str>,
              "Mentions": <int>,
              "Engagement": {
                  "Reactions": <int>,
                  "Comments": <int>,
                  "Shares": <int>,
                  "Views": <int>,
                  "Engagement": <int>
              },
              "Content": [<str>, ...],
              "Date": <str>
          },
          ...
      ]
    }
    """
    # Prepare the list that will hold per-topic details
    output = []

    # Get unique topics from the DataFrame
    topics = df[topic_col].dropna().unique().tolist()

    for t in topics:
        # Filter the DataFrame for the current topic
        topic_df = df[df[topic_col] == t]
        if topic_df.empty:
            # If no data for this topic, just append a dict with empty TopPost
            output.append({"Topic": t, "TopPost": []})
            continue

        # Aggregate data at the post level
        aggregated = (
            topic_df
            .groupby([url_col, title_col, date_col], dropna=False)
            .agg({
                id_col: "count",  # We'll treat each row as 1 mention
                reactions_col: "sum",
                comments_col: "sum",
                shares_col: "sum",
                views_col: "sum"
            })
            .reset_index()
            .rename(columns={id_col: "Mentions"})
        )

        # Compute total engagement = Reactions + Comments + Shares + Views
        aggregated["EngagementSum"] = (
            aggregated[reactions_col]
            + aggregated[comments_col]
            + aggregated[shares_col]
            + aggregated[views_col]
        )

        # Sort by "Mentions" descending
        aggregated.sort_values(by="Mentions", ascending=False, inplace=True)

        # Select top N posts
        top_posts_df = aggregated.head(top_n)

        # Build the list of post objects for the topic
        topic_top_posts = []
        for _, row in top_posts_df.iterrows():
            # Filter back the rows for this specific (UrlTopic, Title, Date)
            matching_df = topic_df[
                (topic_df[url_col] == row[url_col]) &
                (topic_df[title_col] == row[title_col]) &
                (topic_df[date_col] == row[date_col])
            ]

            # Gather up to max_comments unique user comments
            all_comments = matching_df[content_col].dropna().unique().tolist()
            if len(all_comments) > max_comments:
                all_comments = random.sample(all_comments, max_comments)

            # Construct the post object
            post_obj = {
                "UrlTopic": str(row[url_col]) if pd.notnull(row[url_col]) else "",
                "Title": str(row[title_col]) if pd.notnull(row[title_col]) else "",
                "Mentions": int(row["Mentions"]),
                "Engagement": {
                    "Reactions": int(row[reactions_col]),
                    "Comments": int(row[comments_col]),
                    "Shares": int(row[shares_col]),
                    "Views": int(row[views_col]),
                    "Engagement": int(row["EngagementSum"]),
                },
                "Content": all_comments,
                "Date": str(row[date_col]) if pd.notnull(row[date_col]) else "",
            }

            topic_top_posts.append(post_obj)

        # Append this topic's info to the output
        output.append({
            "Topic": str(t),
            "TopPost": topic_top_posts
        })

    return output

#########################################################

def generate_channel_details(
    df,
    params,
    brand_col: str = "Topic",
    channel_col: str = "ChannelDeep",
    url_col: str = "UrlTopic",
    title_col: str = "Title",
    content_col: str = "Content",
    site_col: str = "SiteName",
    sentiment_col: str = "Sentiment",
    reactions_col: str = "Reactions",
    comments_col: str = "Comments",
    shares_col: str = "Shares",
    # For the "Mention" count, we simply use row counts. 
    # If your dataset has a separate "Mentions" column, 
    # you can adapt it here.
) -> dict:
    
    # 1) Identify the single brand name in the dataset.
    #    If you have multiple, pick the first or adapt as needed.
    if df.empty:
        return {"Topic": {"Name": "", "Channels": []}}
    
    # For example, assume there's only one brand in 'brand_col':
    brand_name = df[brand_col].dropna().unique()
    if len(brand_name) > 0:
        brand_name = str(brand_name[0])
    else:
        brand_name = ""

    # Prepare the final output structure
    output = {
        "Topic": {
            "Name": brand_name,
            "Channels": []
        }
    }
    
    # 2) Group by Channel (ChannelDeep) for the brand
    channel_groups = df.groupby(channel_col, dropna=False)
    
    for channel_value, channel_df in channel_groups:
        if pd.isna(channel_value):
            channel_value = "UnknownChannel"

        # ----- 2a) MENTION: total row count for this channel -----
        mention_count = len(channel_df)

        # ----- 2b) SENTIMENT: sum up Positive, Neutral, Negative -----
        # We can simply count rows where sentiment == "Positive", etc.
        positive_count = len(channel_df[channel_df[sentiment_col] == "Positive"])
        neutral_count  = len(channel_df[channel_df[sentiment_col] == "Neutral"])
        negative_count = len(channel_df[channel_df[sentiment_col] == "Negative"])
        
        # ----- 2c) TOP POST for this channel -----
        #   We define "top post" as the one with the highest row count or 
        #   highest total (Reactions + Comments + Shares). 
        #   Let's pick by greatest total engagement for demonstration.
        
        # Group by (UrlTopic, Title, SiteName) 
        # Summation of Reactions, Comments, Shares => total engagement
        # Mentions => row count
        group_top_post = (
            channel_df
            .groupby([url_col, title_col, site_col], dropna=False)
            .agg({
                reactions_col: "sum",
                comments_col: "sum",
                shares_col: "sum",
                # If you have 'Views', add it as well
                "Id": "count"  # or any unique column for counting mentions
            })
            .rename(columns={"Id": "Mentions"})
            .reset_index()
        )
        
        # Calculate engagement
        group_top_post["Engagement"] = (
            group_top_post[reactions_col] 
            + group_top_post[comments_col] 
            + group_top_post[shares_col]
        )
        
        # Sort by engagement descending
        group_top_post = group_top_post.sort_values("Engagement", ascending=False)
        
        if not group_top_post.empty:
            top_post_row = group_top_post.iloc[0]
            top_post_url   = top_post_row[url_col]
            top_post_title = top_post_row[title_col]
            top_post_site  = top_post_row[site_col]
            top_post_mentions = int(top_post_row["Mentions"])
            top_post_engagement = int(top_post_row["Engagement"])
            
            # Collect up to (say) 10 comments from the channel_df 
            # that match this top post
            matching_top_df = channel_df[
                (channel_df[url_col] == top_post_url) & (channel_df[title_col] == top_post_title)
            ]
            top_post_contents = (
                matching_top_df[content_col]
                .dropna()
                .unique()
                .tolist()
            )
            # If you want to limit the number of comments (e.g., 30 max):
            top_post_contents = top_post_contents[:30]
            
            top_post_dict = {
                "UrlTopic": str(top_post_url) if pd.notnull(top_post_url) else "",
                "Title": str(top_post_title) if pd.notnull(top_post_title) else "",
                "Mentions": top_post_mentions,
                "Content": top_post_contents,
                "Engagement": top_post_engagement,
                "SiteName": str(top_post_site) if pd.notnull(top_post_site) else "",
            }
        else:
            # No data found for top post
            top_post_dict = {
                "UrlTopic": "",
                "Title": "",
                "Mentions": 0,
                "Content": [],
                "Engagement": 0,
                "SiteName": "",
            }

        # ----- 2d) top_sites: List of site names sorted by mention in descending order -----
        # Group by SiteName => get mention count => sort
        site_groups = (
            channel_df
            .groupby(site_col, dropna=False)[url_col]
            .count()  # count how many rows/URL references
            .reset_index(name="mentions")
            .sort_values("mentions", ascending=False)
        )
        
        site_list = []
        for _, site_row in site_groups.iterrows():
            site_name_val = site_row[site_col]
            if pd.isna(site_name_val):
                site_name_val = "UnknownSite"
            mention_val = int(site_row["mentions"])
            
            # For each site, gather a list of top posts (UrlTopic & Title)  
            # sorted by mention. 
            site_df = channel_df[channel_df[site_col] == site_row[site_col]]
            site_posts = (
                site_df
                .groupby([url_col, title_col], dropna=False)[
                    [reactions_col, comments_col, shares_col, "Id"]
                ]
                .agg({
                    reactions_col: "sum",
                    comments_col: "sum",
                    shares_col: "sum",
                    "Id": "count"
                })
                .rename(columns={"Id": "Mentions"})
                .reset_index()
            )

            # Sort by Mentions or Engagement, depending on your requirement
            site_posts = site_posts.sort_values("Mentions", ascending=False)
            
            titles = []
            for __, post_row in site_posts.iterrows():
                post_url   = post_row[url_col]
                post_title = post_row[title_col]
                post_mention_count = int(post_row["Mentions"])
                
                # Build a "Title" entry
                titles.append({
                    "UrlTopic": str(post_url) if pd.notnull(post_url) else "",
                    "Title": str(post_title) if pd.notnull(post_title) else "",
                    "Mentions": post_mention_count
                })
            
            site_list.append({
                "SiteName": str(site_name_val),
                "mentions": mention_val,
                "Title": titles  # an array of top posts on that site
            })
        
        # ----- Build the final structure for this channel -----
        channel_obj = {
            "ChannelDeep": str(channel_value),
            "Mention": mention_count,
            "TopPost": top_post_dict,
            "Sentiment": {
                "Positive": positive_count,
                "Neutral":  neutral_count,
                "Negative": negative_count,
            },
            "top_sites": site_list
        }
        
        # Append to the "Channels" list
        output["Topic"]["Channels"].append(channel_obj)
    
    return output



#########################################################################################

def generate_brand_sentiment_details(
    df,
    params,
    brand_col: str = "Topic",
    sentiment_col: str = "Sentiment",  # "Positive", "Neutral", "Negative"
    url_col: str = "UrlTopic",
    title_col: str = "Title",
    date_col: str = "FormattedDate",
    channel_col: str = "ChannelDeep",
    site_col: str = "SiteName",
    content_col: str = "Content",
    max_comments_per_sentiment: int = 100,  # max random comments per brand+sentiment
) -> Dict[str, Any]:
    """
    Processes the DataFrame to extract sentiment details per brand by sampling comments first.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing brand sentiments.
        ... (other parameters as described above)

    Returns:
        dict: A dictionary containing sentiment details structured by brand.
    """
    # Final output
    output = {
        "Topic": []
    }

    # 1) Identify all unique brands
    brands = df[brand_col].dropna().unique().tolist()

    for brand_value in brands:
        # Subset DataFrame for this brand
        brand_df = df[df[brand_col] == brand_value]
        if brand_df.empty:
            continue

        # Build skeleton for this brand
        brand_obj = {
            "Name": str(brand_value),
            "SentimentDetails": {
                "Positive": [],
                "Neutral": [],
                "Negative": []
            }
        }

        # 2) For each sentiment, process comments
        for sentiment_type in ["Positive", "Neutral", "Negative"]:
            senti_df = brand_df[brand_df[sentiment_col] == sentiment_type]
            if senti_df.empty:
                # If no rows for this sentiment, store empty array
                brand_obj["SentimentDetails"][sentiment_type] = []
                continue

            # Total number of mentions for this brand+sentiment############ thêm 1 for cho mỗi sentiment
            total_senti_mentions = len(senti_df)

            # Sample up to max_comments_per_sentiment comments
            sampled_comments = senti_df[content_col].dropna().unique().tolist()
            if len(sampled_comments) > max_comments_per_sentiment:
                sampled_comments = random.sample(sampled_comments, max_comments_per_sentiment)

            # Get the rows corresponding to the sampled comments
            # To ensure we get unique posts, we need to retrieve the posts containing these comments
            sampled_rows = senti_df[senti_df[content_col].isin(sampled_comments)]

            # Group the sampled rows by UrlTopic to reconstruct posts
            grouped = sampled_rows.groupby(url_col, dropna=False)

            post_groups = []
            for urlv, group in grouped:
                # Retrieve post details from the first occurrence in the group
                first_row = group.iloc[0]

                # Count total sentiment mentions for this post across the entire DataFrame
                # This ensures SentimentMentions reflects the total, not just the sampled comments
                post_sentiment_count = brand_df[
                    (brand_df[url_col] == urlv) &
                    (brand_df[sentiment_col] == sentiment_type)
                ].shape[0]

                # Gather unique comments from the sampled group
                contents = group[content_col].dropna().unique().tolist()

                post_groups.append({
                    "UrlTopic":  str(urlv) if pd.notnull(urlv) else "",
                    "Title":     str(first_row[title_col]) if pd.notnull(first_row[title_col]) else "",
                    "Content":   contents,
                    "ChannelDeep": str(first_row[channel_col]) if pd.notnull(first_row[channel_col]) else "",
                    "Date":      str(first_row[date_col]) if pd.notnull(first_row[date_col]) else "",
                    "SiteName":  str(first_row[site_col]) if pd.notnull(first_row[site_col]) else "",
                    "SentimentMentions": post_sentiment_count
                })

            # Limit to max_posts if necessary (optional, based on original max_posts parameter)
            # If you still want to limit the number of posts per sentiment, you can uncomment the following lines:
            max_posts = 30  # Define max_posts or pass as a parameter
            if len(post_groups) > max_posts:
                post_groups = random.sample(post_groups, max_posts)

            # Build final object for this sentiment
            senti_obj = {
                "mentions": total_senti_mentions,
                "PostDetails": post_groups
            }

            # Add to brand's SentimentDetails
            brand_obj["SentimentDetails"][sentiment_type].append(senti_obj)

        # 3) Append this brand to the final output
        output["Topic"].append(brand_obj)

    return output


#########################################################################################

def generate_label_details(
    df,
    params,
    topic_col: str = "Topic",
    label_col: str = "Labels1",
    sentiment_col: str = "Sentiment",   # "Positive", "Neutral", "Negative"
    url_col: str = "UrlTopic",
    title_col: str = "Title",
    content_col: str = "Content",
    channel_col: str = "ChannelDeep",
    date_col: str = "FormattedDate",
    reactions_col: str = "Reactions",
    comments_col: str = "Comments",
    shares_col: str = "Shares",
    views_col: str = "Views",
    id_col: str = "Id",
    max_posts_per_sentiment: int = 20,  # Limit to 20 posts per sentiment
    max_comments_in_post: int = 20      # Limit random sampling of comments within each post
) -> list:
    """
    Returns a list of Topics, each with a "Label" list. 
    For each label:
      - 'Date': a list of all (date, mention_count)
      - 'SentimentDetails': up to 20 posts for each sentiment (Positive, Neutral, Negative).
        The first post in each sentiment includes the 'mentions' key (total for that sentiment).
      - 'TopPost': a single post (highest Mentions) with up to max_comments_in_post comments.
    """

    output = []

    # 1) Unique Topics
    topics = df[topic_col].dropna().unique().tolist()

    for t in topics:
        # Subset for this Topic
        topic_df = df[df[topic_col] == t]
        if topic_df.empty:
            output.append({"Topic": t, "Label": []})
            continue

        topic_dict = {
            "Topic": str(t),
            "Label": []
        }

        # 2) Unique Labels within this Topic
        labels = topic_df[label_col].dropna().unique().tolist()

        for l in labels:
            label_df = topic_df[topic_df[label_col] == l]
            if label_df.empty:
                continue

            # Calculate total Mentions for this label
            label_mentions = len(label_df)

            # Attempt to pick one ChannelDeep (or adapt as needed)
            channel_val = label_df[channel_col].dropna().unique()
            channel_str = str(channel_val[0]) if len(channel_val) > 0 else ""

            # 3) Build the "Date" array
            date_agg = (
                label_df
                .groupby(date_col).size()
                .reset_index(name="mention_count")
            )
            date_list = []
            for _, row_d in date_agg.iterrows():
                date_list.append({
                    "DateofMetions": str(row_d[date_col]),
                    "mentions": int(row_d["mention_count"])
                })

            # 4) SentimentDetails: up to 20 posts per sentiment
            sentiment_details = {
                "Positive": [],
                "Neutral": [],
                "Negative": []
            }

            for sentiment_key in ["Positive", "Neutral", "Negative"]:
                sub_df = label_df[label_df[sentiment_col] == sentiment_key]
                if sub_df.empty:
                    sentiment_details[sentiment_key] = []
                    continue

                # Count total for that sentiment
                sentiment_count = len(sub_df)

                # Group by (UrlTopic, Title, ChannelDeep) to define a "post"
                # Then we can pick up to 20 such "posts"
                grouped_posts = (
                    sub_df
                    .groupby([url_col, title_col, channel_col], dropna=False)
                    .agg({
                        id_col: "count"
                    })
                    .reset_index()
                    .rename(columns={id_col: "Mentions"})
                )

                # Sort by Mentions descending, then take top 20 groups
                grouped_posts.sort_values(by="Mentions", ascending=False, inplace=True)
                top_posts_df = grouped_posts.head(max_posts_per_sentiment)

                # We’ll build one item per "post" in top_posts_df
                items = []
                for idx, grow in top_posts_df.iterrows():
                    # Filter sub_df to get the actual rows for that grouping
                    post_match = sub_df[
                        (sub_df[url_col] == grow[url_col]) &
                        (sub_df[title_col] == grow[title_col]) &
                        (sub_df[channel_col] == grow[channel_col])
                    ]
                    # Gather all content from these rows (randomly sampling if > max_comments_in_post)
                    content_list = post_match[content_col].dropna().unique().tolist()
                    if len(content_list) > max_comments_in_post:
                        content_list = random.sample(content_list, max_comments_in_post)

                    # For the very first item in this sentiment, include 'mentions'
                    if idx == top_posts_df.index[0]:
                        # => if idx == 0 doesn’t always work if we took a slice from top, 
                        #    so we compare the index to the first label in top_posts_df.index
                        item_obj = {
                            "mentions": sentiment_count,  # the total sentiment mentions
                            "UrlTopic":  str(grow[url_col]) if pd.notnull(grow[url_col]) else "",
                            "Title":     str(grow[title_col]) if pd.notnull(grow[title_col]) else "",
                            "ChannelDeep": str(grow[channel_col]) if pd.notnull(grow[channel_col]) else "",
                            "Content":   content_list
                        }
                    else:
                        item_obj = {
                            "UrlTopic":  str(grow[url_col]) if pd.notnull(grow[url_col]) else "",
                            "Title":     str(grow[title_col]) if pd.notnull(grow[title_col]) else "",
                            "ChannelDeep": str(grow[channel_col]) if pd.notnull(grow[channel_col]) else "",
                            "Content":   content_list
                        }

                    items.append(item_obj)

                sentiment_details[sentiment_key] = items

            # 5) Single "TopPost"
            grouped_posts_top = (
                label_df
                .groupby([url_col, title_col], dropna=False)
                .agg({
                    id_col: "count",  # => "Mentions"
                    reactions_col: "sum",
                    comments_col: "sum",
                    shares_col:   "sum",
                    views_col:    "sum"
                })
                .reset_index()
                .rename(columns={id_col: "Mentions"})
            )
            grouped_posts_top["EngagementSum"] = (
                grouped_posts_top[reactions_col]
                + grouped_posts_top[comments_col]
                + grouped_posts_top[shares_col]
                + grouped_posts_top[views_col]
            )
            grouped_posts_top.sort_values(by="Mentions", ascending=False, inplace=True)

            if grouped_posts_top.empty:
                top_post = {
                    "UrlTopic": "",
                    "Title": "",
                    "Mentions": 0,
                    "Engagement": {
                        "Reactions": 0,
                        "Comments": 0,
                        "Shares": 0,
                        "Views": 0,
                        "Engagement": 0
                    },
                    "Content": []
                }
            else:
                best_row = grouped_posts_top.iloc[0]
                best_match = label_df[
                    (label_df[url_col] == best_row[url_col]) &
                    (label_df[title_col] == best_row[title_col])
                ]
                post_comments = best_match[content_col].dropna().unique().tolist()
                # Randomly limit post comments
                if len(post_comments) > max_comments_in_post:
                    post_comments = random.sample(post_comments, max_comments_in_post)

                top_post = {
                    "UrlTopic": str(best_row[url_col]) if pd.notnull(best_row[url_col]) else "",
                    "Title":    str(best_row[title_col]) if pd.notnull(best_row[title_col]) else "",
                    "Mentions": int(best_row["Mentions"]),
                    "Engagement": {
                        "Reactions":   int(best_row[reactions_col]),
                        "Comments":    int(best_row[comments_col]),
                        "Shares":      int(best_row[shares_col]),
                        "Views":       int(best_row[views_col]),
                        "Engagement":  int(best_row["EngagementSum"])
                    },
                    "Content": post_comments
                }

            # 6) Build the final label dictionary
            label_dict = {
                "Value":       str(l),
                "Mentions":    label_mentions,
                "ChannelDeep": channel_str,
                "Date":        date_list,
                "SentimentDetails": sentiment_details,
                "TopPost":     top_post
            }

            topic_dict["Label"].append(label_dict)

        output.append(topic_dict)

    return output

#########################################################################################

def get_daily_detail_data(df, params, brand_col='Topic', date_col='FormattedDate'):
    """
    Build a dictionary with key "daily" containing a list of daily insights 
    for each (brand, date), including:
      - mentions
      - engagement
      - sentiment counts
      - top sites (with sentiment breakdown)
      - top channels (with sentiment breakdown)
      - top posts (with sentiment breakdown)

    Return structure matches the JSON schema given in get_daily_detail function declaration.
    """

    # 1) Ensure numeric columns exist; fill missing with 0
    for col in ['Reactions', 'Comments', 'Shares', 'Views']:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)

    # 2) Ensure 'Sentiment' exists & fill NA
    if 'Sentiment' not in df.columns:
        df['Sentiment'] = 'NA'
    df['Sentiment'] = df['Sentiment'].fillna('NA')

    # 3) Convert date_col to datetime.date if present
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date
    else:
        # If date_col is missing, just store None
        df[date_col] = None

    # ------------------------------------------------------------------
    # A) AGGREGATE brand+date-level data (mentions, engagement, sentiment)
    # ------------------------------------------------------------------
    # A1) brand+date main aggregator
    agg_main = (
        df
        .groupby([brand_col, date_col], dropna=True)
        .agg({
            'Id':        'count',    # = number of rows => mentions
            'Reactions': 'sum',
            'Comments':  'sum',
            'Shares':    'sum',
            'Views':     'sum'
        })
        .reset_index()
        .rename(columns={'Id': 'mentions'})
    )
    agg_main['engagement'] = (
        agg_main['Reactions'] +
        agg_main['Comments'] +
        agg_main['Shares']   +
        agg_main['Views']
    )

    # A2) brand+date+sentiment aggregator
    agg_sentiment = (
        df
        .groupby([brand_col, date_col, 'Sentiment'])
        .size()
        .reset_index(name='Count')
    )
    pivot_sentiment = agg_sentiment.pivot_table(
        index=[brand_col, date_col],
        columns='Sentiment',
        values='Count',
        fill_value=0
    ).reset_index()

    # Ensure Negative / Neutral / Positive columns exist
    for needed_col in ['Negative','Neutral','Positive']:
        if needed_col not in pivot_sentiment.columns:
            pivot_sentiment[needed_col] = 0

    # Merge main aggregator + sentiment pivot
    merged_main = pd.merge(
        agg_main,
        pivot_sentiment,
        on=[brand_col, date_col],
        how='left'
    )

    # ------------------------------------------------------------------
    # B) For site-level sentiment, we do brand+date+site+sentiment
    # ------------------------------------------------------------------
    site_agg = (
        df
        .groupby([brand_col, date_col, 'SiteName', 'Sentiment'])
        .size()
        .reset_index(name='Count')
    )
    # We'll store it in a dict-of-dicts so we can quickly look up 
    # sentiment counts by (brand, date, site).
    # e.g. site_sentiment_dict[(brand_val, date_val, siteName)] = {"Positive": x, "Neutral": y, "Negative": z}
    site_sentiment_dict = {}
    for _, row in site_agg.iterrows():
        b = row[brand_col]
        d = row[date_col]
        s = row['SiteName']
        sent = row['Sentiment']
        c   = row['Count']

        key = (b, d, s)
        if key not in site_sentiment_dict:
            site_sentiment_dict[key] = {"Positive": 0, "Neutral": 0, "Negative": 0}
        if sent in ["Positive","Neutral","Negative"]:
            site_sentiment_dict[key][sent] = c

    # For site mention count (regardless of sentiment), just group brand+date+site => size
    site_mentions_agg = (
        df
        .groupby([brand_col, date_col, 'SiteName'])
        .size()
        .reset_index(name='mention_count')
    )
    # We'll build a dictionary of site => mention_count
    site_mentions_dict = {}
    for _, row in site_mentions_agg.iterrows():
        b = row[brand_col]
        d = row[date_col]
        s = row['SiteName']
        cnt = row['mention_count']
        site_mentions_dict[(b,d,s)] = cnt

    # ------------------------------------------------------------------
    # C) For channel-level sentiment, brand+date+ChannelDeep+sentiment
    # ------------------------------------------------------------------
    channel_agg = (
        df
        .groupby([brand_col, date_col, 'ChannelDeep', 'Sentiment'])
        .size()
        .reset_index(name='Count')
    )
    channel_sentiment_dict = {}
    for _, row in channel_agg.iterrows():
        b = row[brand_col]
        d = row[date_col]
        c = row['ChannelDeep']
        s = row['Sentiment']
        cnt = row['Count']

        key = (b, d, c)
        if key not in channel_sentiment_dict:
            channel_sentiment_dict[key] = {"Positive": 0, "Neutral": 0, "Negative": 0}
        if s in ["Positive","Neutral","Negative"]:
            channel_sentiment_dict[key][s] = cnt

    # brand+date+channel => mention_count
    channel_mentions_agg = (
        df
        .groupby([brand_col, date_col, 'ChannelDeep'])
        .size()
        .reset_index(name='mention_count')
    )
    channel_mentions_dict = {}
    for _, row in channel_mentions_agg.iterrows():
        b = row[brand_col]
        d = row[date_col]
        c = row['ChannelDeep']
        mention_ct = row['mention_count']
        channel_mentions_dict[(b,d,c)] = mention_ct

    # ------------------------------------------------------------------
    # D) For top posts (with sentiment breakdown), brand+date+ParentId+sentiment
    # ------------------------------------------------------------------
    post_agg = (
        df
        .groupby([brand_col, date_col, 'ParentId', 'Sentiment'])
        .size()
        .reset_index(name='Count')
    )
    post_sentiment_dict = {}
    for _, row in post_agg.iterrows():
        b = row[brand_col]
        d = row[date_col]
        pid = row['ParentId']
        s = row['Sentiment']
        cnt = row['Count']

        key = (b, d, pid)
        if key not in post_sentiment_dict:
            post_sentiment_dict[key] = {"Positive": 0, "Neutral": 0, "Negative": 0}
        if s in ["Positive","Neutral","Negative"]:
            post_sentiment_dict[key][s] = cnt

    # For post mentions + engagement, brand+date+ParentId => sum
    post_main_agg = (
        df
        .groupby([brand_col, date_col, 'ParentId'])
        .agg({
            'Id':        'count',
            'Reactions': 'sum',
            'Comments':  'sum',
            'Shares':    'sum',
            'Views':     'sum'
        })
        .reset_index()
        .rename(columns={'Id': 'mention_count'})
    )
    post_main_agg['engagement_sum'] = (
        post_main_agg['Reactions']
        + post_main_agg['Comments']
        + post_main_agg['Shares']
        + post_main_agg['Views']
    )

    # We'll need Title and UrlTopic from the first row with that ParentId
    # Let's keep them in a dictionary for quick lookup.
    title_lookup = {}
    url_lookup   = {}
    # Because we might have multiple rows with the same ParentId, pick the first
    # row (or any row).
    df_sorted = df.sort_values(by=['ParentId','Id'])  # just to ensure a stable order
    for _, row in df_sorted.iterrows():
        pid = row.get('ParentId', None)
        if pid not in title_lookup:
            title_lookup[pid] = row.get('Title', None)
            url_lookup[pid]   = row.get('UrlTopic', None)

    # Convert post_main_agg to a dictionary keyed by (brand, date)
    # with a list of posts
    from collections import defaultdict
    post_data_dict = defaultdict(list)
    for _, row in post_main_agg.iterrows():
        b = row[brand_col]
        d = row[date_col]
        pid   = row['ParentId']
        m_cnt = int(row['mention_count'])
        e_sum = int(row['engagement_sum'])

        # get sentiment breakdown from post_sentiment_dict
        pos_ct = post_sentiment_dict.get((b,d,pid), {}).get("Positive", 0)
        neu_ct = post_sentiment_dict.get((b,d,pid), {}).get("Neutral", 0)
        neg_ct = post_sentiment_dict.get((b,d,pid), {}).get("Negative", 0)

        post_data_dict[(b,d)].append({
            "parentId":     str(pid),  # cast to string for schema
            "title":        title_lookup.get(pid, None) or "",
            "engagement":   e_sum,
            "mentions":     m_cnt,
            "urlTopic":     url_lookup.get(pid, None) or "",
            "sentiment_pos": str(pos_ct),
            "sentiment_neu": str(neu_ct),
            "sentiment_neg": str(neg_ct),
        })

    # ------------------------------------------------------------------
    # E) Build the final list of daily items
    # ------------------------------------------------------------------
    daily_list = []

    for _, row in merged_main.iterrows():
        b = row[brand_col]         # brand
        d = row[date_col]          # date
        mention = int(row['mentions'])
        engagement = int(row['engagement'])
        pos_ct = int(row['Positive'])
        neu_ct = int(row['Neutral'])
        neg_ct = int(row['Negative'])

        # 1) Gather top_sites: we need siteName + mention_count + sentiment
        #    We'll use site_mentions_dict & site_sentiment_dict for brand/date
        #    Then we'll sort in descending order of mention_count
        sub_sites = []
        # collect all sites for (b,d,*)
        for (bb,dd,s_name) in site_mentions_dict.keys():
            if bb == b and dd == d:
                mention_count = site_mentions_dict[(bb,dd,s_name)]
                sent_pos = site_sentiment_dict.get((bb,dd,s_name),{}).get("Positive", 0)
                sent_neu = site_sentiment_dict.get((bb,dd,s_name),{}).get("Neutral", 0)
                sent_neg = site_sentiment_dict.get((bb,dd,s_name),{}).get("Negative", 0)

                sub_sites.append({
                    "siteName":       s_name,
                    "mentions":       mention_count,
                    "sentiment_pos":  str(sent_pos),
                    "sentiment_neu":  str(sent_neu),
                    "sentiment_neg":  str(sent_neg),
                })
        # sort sub_sites descending by "mentions"
        sub_sites.sort(key=lambda x: x['mentions'], reverse=True)

        # 2) Gather top_channels
        sub_channels = []
        for (bb,dd,ch_name) in channel_mentions_dict.keys():
            if bb == b and dd == d:
                mention_count = channel_mentions_dict[(bb,dd,ch_name)]
                sent_pos = channel_sentiment_dict.get((bb,dd,ch_name),{}).get("Positive", 0)
                sent_neu = channel_sentiment_dict.get((bb,dd,ch_name),{}).get("Neutral", 0)
                sent_neg = channel_sentiment_dict.get((bb,dd,ch_name),{}).get("Negative", 0)

                sub_channels.append({
                    "channelDeep":    ch_name,
                    "mentions":       mention_count,
                    "sentiment_pos":  str(sent_pos),
                    "sentiment_neu":  str(sent_neu),
                    "sentiment_neg":  str(sent_neg),
                })
        sub_channels.sort(key=lambda x: x['mentions'], reverse=True)

        # 3) Gather top_posts
        #    post_data_dict[(b,d)] is a list of all posts => we can pick top 5 by mention or engagement
        all_posts = post_data_dict.get((b,d), [])
        # let's pick top 5 by mention_count (or choose another metric if desired)
        all_posts.sort(key=lambda x: x['mentions'], reverse=True)
        top_posts = all_posts[:5]

        # 4) Build daily item
        daily_item = {
            "datetime.date":  d.isoformat() if d else None,  # store as YYYY-MM-DD string
            "Topic":          b,
            "Mention":        mention,
            "engagement":     engagement,
            # casting sentiment to string to match your schema
            "sentiment_pos":  str(pos_ct),
            "sentiment_neu":  str(neu_ct),
            "sentiment_neg":  str(neg_ct),
            "top_sites":      sub_sites,
            "top_channels":   sub_channels,
            "top_posts":      top_posts
        }

        daily_list.append(daily_item)

    # 5) Return the final dictionary that matches your schema:
    return {
        "daily": daily_list
    }
