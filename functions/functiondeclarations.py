from vertexai.generative_models import (
    FunctionDeclaration,
)
brand_health_overview = FunctionDeclaration(
    name="brand_health_overview",
    description=(
        "Provide an overview of brand health for one or more brands, "
        "including sentiment percentages, mentions by date, and mentions by channel in social listening data."
    ),
    parameters={
        "type": "object",
        "properties": {
            "Topics": {
                "type": "object",
                "description": "An object containing a list of brands with their health details.",
                "properties": {
                    "Brands": {
                        "type": "array",
                        "description": "A list of brand health detail objects.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Topic": {
                                    "type": "string",
                                    "description": "Brand name"
                                },
                                "Sentiment": {
                                    "type": "object",
                                    "description": "Sentiment percentage of the brand, including positive, negative, and neutral.",
                                    "properties": {
                                        "Positive": {
                                            "type": "number",
                                            "description": "Percentage of positive sentiment."
                                        },
                                        "Neutral": {
                                            "type": "number",
                                            "description": "Percentage of neutral sentiment."
                                        },
                                        "Negative": {
                                            "type": "number",
                                            "description": "Percentage of negative sentiment."
                                        }
                                    },
                                    "required": ["Positive", "Neutral", "Negative"]
                                },
                                "MentionsByDate": {
                                    "type": "array",
                                    "description": "Total mentions of the brand grouped by date.",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "Date": {
                                                "type": "string",
                                                "format": "date",
                                                "description": "Date in ISO 8601 format (YYYY-MM-DD)."
                                            },
                                            "Mention": {
                                                "type": "number",
                                                "description": "Total mentions of the brand on the specified date."
                                            }
                                        },
                                        "required": ["Date", "Mention"]
                                    }
                                },
                                "MentionsByChannel": {
                                    "type": "array",
                                    "description": "Total mentions of the brand grouped by channel.",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "ChannelDeep": {
                                                "type": "string",
                                                "description": (
                                                    "Channel name on social media, including Facebook User, Facebook Group, "
                                                    "Facebook Page, Fanpage, Youtube, Tiktok, News, Forum, Instagram, Others."
                                                )
                                            },
                                            "Mention": {
                                                "type": "number",
                                                "description": "Total mentions of the brand on the specified channel."
                                            }
                                        },
                                        "required": ["ChannelDeep", "Mention"]
                                    }
                                },
                                "SocialPostOverview": {
                                    "type": "object",
                                    "description": (
                                        "Metrics about social posts, including number of unique posts, number of comments, "
                                        "comment/post ratio, not including news."
                                    ),
                                    "properties": {
                                        "NumberofPost": {
                                            "type": "number",
                                            "description": "Number of social posts, not including news."
                                        },
                                        "NumberofComment": {
                                            "type": "number",
                                            "description": "Number of relevant comments on the social posts."
                                        },
                                        "CommentPostRatio": {
                                            "type": "number",
                                            "description": "Comment to post ratio."
                                        }
                                    },
                                    "required": ["NumberofPost", "NumberofComment", "CommentPostRatio"]
                                },
                                "Engagement": {
                                    "type": "object",
                                    "description": "Engagement metrics of the brand on social media.",
                                    "properties": {
                                        "NumberofPost": {
                                            "type": "number",
                                            "description": "Number of social posts, not including news."
                                        },
                                        "Reactions": {
                                            "type": "number",
                                            "description": "Total reactions of the brand on social media."
                                        },
                                        "ReactionsRate": {
                                            "type": "number",
                                            "description": "Reactions rate of the brand on social media."
                                        },
                                        "Comments": {
                                            "type": "number",
                                            "description": "Total comments of the brand on social media."
                                        },
                                        "CommentsRate": {
                                            "type": "number",
                                            "description": "Comments rate of the brand on social media."
                                        },
                                        "Shares": {
                                            "type": "number",
                                            "description": "Total shares of the brand on social media."
                                        },
                                        "SharesRate": {
                                            "type": "number",
                                            "description": "Shares rate of the brand on social media."
                                        },
                                        "Views": {
                                            "type": "number",
                                            "description": "Total views of the brand on social media."
                                        },
                                        "ViewsRate": {
                                            "type": "number",
                                            "description": "Views rate of the brand on social media."
                                        },
                                        "Engagement": {
                                            "type": "number",
                                            "description": "Total engagement of the brand on social media."
                                        },
                                        "EngagementRate": {
                                            "type": "number",
                                            "description": "Engagement rate of the brand on social media."
                                        }
                                    },
                                    "required": [
                                        "NumberofPost", "Reactions", "ReactionsRate",
                                        "Comments", "CommentsRate", "Shares",
                                        "SharesRate", "Views", "ViewsRate",
                                        "Engagement", "EngagementRate"
                                    ]
                                }
                            },
                            "required": [
                                "Topic", "Sentiment", "MentionsByDate", "MentionsByChannel",
                                "SocialPostOverview", "Engagement"
                            ]
                        }
                    }
                }
            }
        },
        "required": ["Topics"]
    },
)


get_top_post_details = FunctionDeclaration(
    name="get_top_post_details",
    description=(
        "Get details about the top posts for multiple Topics, "
        "including mentions, engagement, and user comments."
    ),
    parameters={
        "type": "object",
        "description": "An object containing a list of topics with their respective top posts.",
        "properties": {
            "Topics": {  # Encapsulate topics within a single object property
                "type": "array",
                "description": "A list of objects, each containing a Topic name and its list of top posts.",
                "items": {
                    "type": "object",
                    "description": "Details of a specific Topic and its top posts.",
                    "properties": {
                        "Topic": {
                            "type": "string",
                            "description": "Brand or campaign name."
                        },
                        "TopPost": {
                            "type": "array",
                            "description": "An array (up to 20) of top posts for the topic (brand/campaign).",
                            "items": {
                                "type": "object",
                                "description": "Details of a single top post for a specific Topic.",
                                "properties": {
                                    "UrlTopic": {
                                        "type": "string",
                                        "description": "Link to the post."
                                    },
                                    "Title": {
                                        "type": "string",
                                        "description": "The main text or headline of the post."
                                    },
                                    "Mentions": {
                                        "type": "number",
                                        "description": "Total number of mentions for the post."
                                    },
                                    "Engagement": {
                                        "type": "object",
                                        "description": (
                                            "Detailed metrics on post engagement, including reactions, "
                                            "comments, shares, and views."
                                        ),
                                        "properties": {
                                            "Reactions": {
                                                "type": "number",
                                                "description": "Total reactions on social media."
                                            },
                                            "Comments": {
                                                "type": "number",
                                                "description": "Total comments on social media."
                                            },
                                            "Shares": {
                                                "type": "number",
                                                "description": "Total shares on social media."
                                            },
                                            "Views": {
                                                "type": "number",
                                                "description": "Total views on social media."
                                            },
                                            "Engagement": {
                                                "type": "number",
                                                "description": (
                                                    "Sum of reactions, comments, shares, and views "
                                                    "(total engagement)."
                                                )
                                            }
                                        },
                                        "required": [
                                            "Reactions",
                                            "Comments",
                                            "Shares",
                                            "Views",
                                            "Engagement"
                                        ]
                                    },
                                    "Content": {
                                        "type": "array",
                                        "description": "List of user comments associated with the post.",
                                        "items": {
                                            "type": "string",
                                            "description": "A single user comment."
                                        },
                                        "maxItems": 100  # Optional: limit the number of comments
                                    },
                                    "Date": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "Date in ISO 8601 format (YYYY-MM-DD)."
                                    }
                                },
                                "required": [
                                    "UrlTopic",
                                    "Title",
                                    "Mentions",
                                    "Engagement",
                                    "Content",
                                    "Date"
                                ]
                            },
                            "maxItems": 20  # Limit to 20 top posts
                        }
                    },
                    "required": [
                        "Topic",
                        "TopPost"
                    ]
                }
            }
        },
        "required": ["Topics"]
    }
)


get_channel_detail = FunctionDeclaration(
    name="get_channel_detail",
    description=(
        "Get each brand's total mentions, top posts, and sentiment data for all channels in the dataset."
    ),
    parameters={
        "type": "object",
        "properties": {
            "Topics": {
                "type": "array",
                "description": "A list of brands with their respective channel details.",
                "items": {
                    "type": "object",
                    "description": "Details for a specific brand.",
                    "properties": {
                        "Name": {
                            "type": "string",
                            "description": "Brand name."
                        },
                        "Channels": {
                            "type": "array",
                            "description": "List of channels and their respective details.",
                            "items": {
                                "type": "object",
                                "description": "Details for a specific channel.",
                                "properties": {
                                    "ChannelDeep": {
                                        "type": "string",
                                        "description": (
                                            "Channel name on social media, including Facebook User, Facebook Group, "
                                            "Facebook Page, Fanpage, Youtube, Tiktok, News, Forum, Instagram, Others."
                                        ),
                                    },
                                    "Mention": {
                                        "type": "number",
                                        "description": "Total mentions of the Topic (brand) on the channel.",
                                    },
                                    "TopPost": {
                                        "type": "array",
                                        "description": "An array (up to 20) of top posts for the channel.",
                                        "items": {
                                            "type": "object",
                                            "description": "Details of a single top post for the channel.",
                                            "properties": {
                                                "UrlTopic": {
                                                    "type": "string",
                                                    "description": "URL of the top post.",
                                                },
                                                "Title": {
                                                    "type": "string",
                                                    "description": "Content of the top post.",
                                                },
                                                "Mentions": {
                                                    "type": "number",
                                                    "description": "Total mentions of the top post.",
                                                },
                                                "Content": {
                                                    "type": "array",
                                                    "description": "List of user comments associated with the top post.",
                                                    "items": {
                                                        "type": "string",
                                                        "description": "A single user comment.",
                                                    },
                                                    "maxItems": 100  # Optional: limit the number of comments
                                                },
                                                "Engagement": {
                                                    "type": "number",
                                                    "description": "Total engagement (likes, shares, comments) on the top post.",
                                                },
                                                "SiteName": {
                                                    "type": "string",
                                                    "description": "Name of the site where the top post was shared.",
                                                },
                                            },
                                            "required": [
                                                "UrlTopic",
                                                "Title",
                                                "Mentions",
                                                "Content",
                                                "Engagement",
                                                "SiteName"
                                            ]
                                        },
                                        "maxItems": 20  # Limit to 20 top posts
                                    },
                                    "Sentiment": {
                                        "type": "object",
                                        "description": "Sentiment analysis data for the channel.",
                                        "properties": {
                                            "Positive": {
                                                "type": "number",
                                                "description": "Number of positive mentions.",
                                            },
                                            "Neutral": {
                                                "type": "number",
                                                "description": "Number of neutral mentions.",
                                            },
                                            "Negative": {
                                                "type": "number",
                                                "description": "Number of negative mentions.",
                                            },
                                        },
                                        "required": ["Positive", "Neutral", "Negative"]
                                    },
                                    "top_sites": {
                                        "type": "array",
                                        "description": "List of site names sorted by total mentions in descending order.",
                                        "items": {
                                            "type": "object",
                                            "description": "Details of a top site.",
                                            "properties": {
                                                "SiteName": {
                                                    "type": "string",
                                                    "description": "Name of the site."
                                                },
                                                "mentions": {
                                                    "type": "number",
                                                    "description": "Total mentions on the site."
                                                },
                                                "Title": {
                                                    "type": "array",
                                                    "description": "List of top posts on that site.",
                                                    "items": {
                                                        "type": "object",
                                                        "description": "Details of a single top post on the site.",
                                                        "properties": {
                                                            "UrlTopic": {
                                                                "type": "string",
                                                                "description": "URL of the top post.",
                                                            },
                                                            "Title": {
                                                                "type": "string",
                                                                "description": "Content of the top post.",
                                                            },
                                                            "Mentions": {
                                                                "type": "number",
                                                                "description": "Total mentions of the top post.",
                                                            },
                                                        },
                                                        "required": [
                                                            "UrlTopic",
                                                            "Title",
                                                            "Mentions"
                                                        ]
                                                    },
                                                    "maxItems": 20  # Optional: limit number of top posts per site
                                                },
                                            },
                                            "required": ["SiteName", "mentions", "Title"]
                                        }
                                    },
                                },
                                "required": [
                                    "ChannelDeep",
                                    "Mention",
                                    "TopPost",
                                    "Sentiment",
                                    "top_sites"
                                ]
                            },
                        },
                    },
                    "required": [
                        "Name",
                        "Channels"
                    ]
                }
            }
        },
        "required": ["Topics"]
    }
)


get_brand_sentiment_detail = FunctionDeclaration(
    name="get_brand_sentiment_detail",
    description=(
        "Return sentiment details of brands in social listening data, "
        "with user comments and sentiment background."
    ),
    parameters={
        "type": "object",
        "properties": {
            "Topics": {  # Renamed from "Topic" to "Topics" to reflect multiple brands
                "type": "array",
                "description": "A list of objects, each containing details for a single brand.",
                "items": {
                    "type": "object",
                    "description": "Details for a single brand.",
                    "properties": {
                        "Name": {
                            "type": "string",
                            "description": "Brand name."
                        },
                        "SentimentDetails": {
                            "type": "object",
                            "description": "Detailed sentiment breakdown with content and context.",
                            "properties": {
                                "Positive": {
                                    "type": "array",
                                    "description": "Details of positive mentions for the brand, grouped by multiple UrlTopics.",
                                    "items": {
                                        "type": "object",
                                        "description": "One grouping of positive sentiment for a single UrlTopic.",
                                        "properties": {
                                            "mentions": {
                                                "type": "number",
                                                "description": "Total number of positive mentions for this brand."
                                            },
                                            "PostDetails": {
                                                "type": "array",
                                                "description": "Details of the top posts for this sentiment.",
                                                "items": {
                                                    "type": "object",
                                                    "description": "Single post detail object for positive sentiment.",
                                                    "properties": {
                                                        "UrlTopic": {
                                                            "type": "string",
                                                            "description": "URL or unique identifier (optional)."
                                                        },
                                                        "Title": {
                                                            "type": "string",
                                                            "description": "A single title or summary for this UrlTopic."
                                                        },
                                                        "Content": {
                                                            "type": "array",
                                                            "description": "List of user comments/mentions about this UrlTopic.",
                                                            "items": {
                                                                "type": "string",
                                                                "description": "A single user comment."
                                                            },
                                                            "maxItems": 100  # Optional: limit the number of comments
                                                        },
                                                        "ChannelDeep": {
                                                            "type": "string",
                                                            "description": "Channel associated with this UrlTopic."
                                                        },
                                                        "Date": {
                                                            "type": "string",
                                                            "format": "date",
                                                            "description": "Date of the post."
                                                        },
                                                        "SiteName": {
                                                            "type": "string",
                                                            "description": "Name of the site."
                                                        },
                                                        "SentimentMentions": {
                                                            "type": "number",
                                                            "description": "Total number of positive mentions in this post."
                                                        }
                                                    },
                                                    "required": [
                                                        "UrlTopic",
                                                        "Title",
                                                        "Content",
                                                        "ChannelDeep",
                                                        "Date",
                                                        "SiteName",
                                                        "SentimentMentions"
                                                    ]
                                                },
                                                "maxItems": 20  # Optional: limit the number of top posts
                                            }
                                        },
                                        "required": [
                                            "mentions",
                                            "PostDetails"
                                        ]
                                    }
                                },
                                "Neutral": {
                                    "type": "array",
                                    "description": "Details of neutral mentions for the brand, grouped by multiple UrlTopics.",
                                    "items": {
                                        "type": "object",
                                        "description": "One grouping of neutral sentiment for a single UrlTopic.",
                                        "properties": {
                                            "mentions": {
                                                "type": "number",
                                                "description": "Total number of neutral mentions for this brand."
                                            },
                                            "PostDetails": {
                                                "type": "array",
                                                "description": "Details of the top posts for this sentiment.",
                                                "items": {
                                                    "type": "object",
                                                    "description": "Single post detail object for neutral sentiment.",
                                                    "properties": {
                                                        "UrlTopic": {
                                                            "type": "string",
                                                            "description": "URL or unique identifier (optional)."
                                                        },
                                                        "Title": {
                                                            "type": "string",
                                                            "description": "A single title or summary for this UrlTopic."
                                                        },
                                                        "Content": {
                                                            "type": "array",
                                                            "description": "List of user comments/mentions about this UrlTopic.",
                                                            "items": {
                                                                "type": "string",
                                                                "description": "A single user comment."
                                                            },
                                                            "maxItems": 100  # Optional: limit the number of comments
                                                        },
                                                        "ChannelDeep": {
                                                            "type": "string",
                                                            "description": "Channel associated with this UrlTopic."
                                                        },
                                                        "Date": {
                                                            "type": "string",
                                                            "format": "date",
                                                            "description": "Date of the post."
                                                        },
                                                        "SiteName": {
                                                            "type": "string",
                                                            "description": "Name of the site."
                                                        },
                                                        "SentimentMentions": {
                                                            "type": "number",
                                                            "description": "Total number of neutral mentions in this post."
                                                        }
                                                    },
                                                    "required": [
                                                        "UrlTopic",
                                                        "Title",
                                                        "Content",
                                                        "ChannelDeep",
                                                        "Date",
                                                        "SiteName",
                                                        "SentimentMentions"
                                                    ]
                                                },
                                                "maxItems": 20  # Optional: limit the number of top posts
                                            }
                                        },
                                        "required": [
                                            "mentions",
                                            "PostDetails"
                                        ]
                                    }
                                },
                                "Negative": {
                                    "type": "array",
                                    "description": "Details of negative mentions for the brand, grouped by multiple UrlTopics.",
                                    "items": {
                                        "type": "object",
                                        "description": "One grouping of negative sentiment for a single UrlTopic.",
                                        "properties": {
                                            "mentions": {
                                                "type": "number",
                                                "description": "Total number of negative mentions for this brand."
                                            },
                                            "PostDetails": {
                                                "type": "array",
                                                "description": "Details of the top posts for this sentiment.",
                                                "items": {
                                                    "type": "object",
                                                    "description": "Single post detail object for negative sentiment.",
                                                    "properties": {
                                                        "UrlTopic": {
                                                            "type": "string",
                                                            "description": "URL or unique identifier (optional)."
                                                        },
                                                        "Title": {
                                                            "type": "string",
                                                            "description": "A single title or summary for this UrlTopic."
                                                        },
                                                        "Content": {
                                                            "type": "array",
                                                            "description": "List of user comments/mentions about this UrlTopic.",
                                                            "items": {
                                                                "type": "string",
                                                                "description": "A single user comment."
                                                            },
                                                            "maxItems": 100  # Optional: limit the number of comments
                                                        },
                                                        "ChannelDeep": {
                                                            "type": "string",
                                                            "description": "Channel associated with this UrlTopic."
                                                        },
                                                        "Date": {
                                                            "type": "string",
                                                            "format": "date",
                                                            "description": "Date of the post."
                                                        },
                                                        "SiteName": {
                                                            "type": "string",
                                                            "description": "Name of the site."
                                                        },
                                                        "SentimentMentions": {
                                                            "type": "number",
                                                            "description": "Total number of negative mentions in this post."
                                                        }
                                                    },
                                                    "required": [
                                                        "UrlTopic",
                                                        "Title",
                                                        "Content",
                                                        "ChannelDeep",
                                                        "Date",
                                                        "SiteName",
                                                        "SentimentMentions"
                                                    ]
                                                },
                                                "maxItems": 20  # Optional: limit the number of top posts
                                            }
                                        },
                                        "required": [
                                            "mentions",
                                            "PostDetails"
                                        ]
                                    }
                                }
                            },
                            "required": ["Positive", "Neutral", "Negative"]
                        }
                    },
                    "required": [
                        "Name",
                        "SentimentDetails"
                    ]
                }
            }
        },
        "required": ["Topics"]
    }
)


get_label_details = FunctionDeclaration(
    name="get_label_details",
    description="Return details about each Topic and its list of Labels (main topics of brands), including sentiment breakdown, mentions, channel, and top post, grouped by multiple UrlTopics.",
    parameters={
        "type": "object",
        "description": "A list of Topics, each with a 'Topic' name and a list of Labels, including sentiment breakdown, mentions, channel, and top post details.",
        "properties": {
            "Topics": {
                "type": "array",
                "description": "A list of Topics.",
                "items": {
                    "type": "object",
                    "description": "Details for a single Topic and its labels.",
                    "properties": {
                        "Topic": {
                            "type": "string",
                            "description": "The brand or campaign name (the main topic)."
                        },
                        "Label": {
                            "type": "array",
                            "description": "A list of labels, each with relevant information.",
                            "items": {
                                "type": "object",
                                "description": "Details for a single label.",
                                "properties": {
                                    "Value": {
                                        "type": "string",
                                        "description": "The label name/value."
                                    },
                                    "Mentions": {
                                        "type": "number",
                                        "description": "Total mentions associated with this label."
                                    },
                                    "ChannelDeep": {
                                        "type": "string",
                                        "description": "Channel associated at the label level."
                                    },
                                    "Date": {
                                        "type": "object",
                                        "description": "Dates of the label.",
                                        "properties": {
                                            "DateofMetions": {
                                                "type": "string",
                                                "format": "date",
                                                "description": "Date in ISO 8601 format (YYYY-MM-DD)."
                                            },
                                            "mentions": {
                                                "type": "number",
                                                "description": "Number of mentions in each date."
                                            }
                                        }
                                    },
                                    "SentimentDetails": {
                                        "type": "object",
                                        "description": "Detailed sentiment breakdown for the label, grouped by multiple UrlTopics.",
                                        "properties": {
                                            "Positive": {
                                                "type": "array",
                                                "description": "Details of positive mentions for this label.",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "mentions": {
                                                            "type": "number",
                                                            "description": "Number of mentions for this UrlTopic."
                                                        },
                                                        "UrlTopic": {
                                                            "type": "string",
                                                            "description": "URL or unique identifier for this group (optional)."
                                                        },
                                                        "Title": {
                                                            "type": "string",
                                                            "description": "A single title or summary for this UrlTopic."
                                                        },
                                                        "Content": {
                                                            "type": "array",
                                                            "description": "List of user comments/mentions about this UrlTopic.",
                                                            "items": {
                                                                "type": "string",
                                                                "description": "A single user comment."
                                                            }
                                                        },
                                                        "ChannelDeep": {
                                                            "type": "string",
                                                            "description": "Channel associated with this UrlTopic."
                                                        }
                                                    }
                                                }
                                            },
                                            "Neutral": {
                                                "type": "array",
                                                "description": "Details of neutral mentions for this label.",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "mentions": {
                                                            "type": "number",
                                                            "description": "Number of mentions for this UrlTopic."
                                                        },
                                                        "UrlTopic": {
                                                            "type": "string",
                                                            "description": "URL or unique identifier for this group (optional)."
                                                        },
                                                        "Title": {
                                                            "type": "string",
                                                            "description": "A single title or summary for this UrlTopic."
                                                        },
                                                        "Content": {
                                                            "type": "array",
                                                            "description": "List of user comments/mentions about this UrlTopic.",
                                                            "items": {
                                                                "type": "string",
                                                                "description": "A single user comment."
                                                            }
                                                        },
                                                        "ChannelDeep": {
                                                            "type": "string",
                                                            "description": "Channel associated with this UrlTopic."
                                                        }
                                                    }
                                                }
                                            },
                                            "Negative": {
                                                "type": "array",
                                                "description": "Details of negative mentions for this label.",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "mentions": {
                                                            "type": "number",
                                                            "description": "Number of mentions for this UrlTopic."
                                                        },
                                                        "UrlTopic": {
                                                            "type": "string",
                                                            "description": "URL or unique identifier for this group (optional)."
                                                        },
                                                        "Title": {
                                                            "type": "string",
                                                            "description": "A single title or summary for this UrlTopic."
                                                        },
                                                        "Content": {
                                                            "type": "array",
                                                            "description": "List of user comments/mentions about this UrlTopic.",
                                                            "items": {
                                                                "type": "string",
                                                                "description": "A single user comment."
                                                            }
                                                        },
                                                        "ChannelDeep": {
                                                            "type": "string",
                                                            "description": "Channel associated with this UrlTopic."
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "TopPost": {
                                        "type": "object",
                                        "description": "Details of the top post for this label.",
                                        "properties": {
                                            "UrlTopic": {
                                                "type": "string",
                                                "description": "Link of the post."
                                            },
                                            "Title": {
                                                "type": "string",
                                                "description": "The main content or title of the post."
                                            },
                                            "Mentions": {
                                                "type": "number",
                                                "description": "Total mentions for this top post."
                                            },
                                            "Engagement": {
                                                "type": "object",
                                                "description": "Detailed metrics on post engagement.",
                                                "properties": {
                                                    "Reactions": {
                                                        "type": "number",
                                                        "description": "Total reactions on the post."
                                                    },
                                                    "Comments": {
                                                        "type": "number",
                                                        "description": "Total comments on the post."
                                                    },
                                                    "Shares": {
                                                        "type": "number",
                                                        "description": "Total shares of the post."
                                                    },
                                                    "Views": {
                                                        "type": "number",
                                                        "description": "Total views of the post."
                                                    },
                                                    "Engagement": {
                                                        "type": "number",
                                                        "description": "Sum of reactions, comments, shares, and views for the post."
                                                    }
                                                }
                                            },
                                            "Content": {
                                                "type": "array",
                                                "description": "List of user comments associated with this top post.",
                                                "items": {
                                                    "type": "string",
                                                    "description": "A single user comment."
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)

get_daily_detail = FunctionDeclaration(
    name="get_daily_detail",
    description="Get brand-level daily detail insights across all dates from the daily_data structure.",
    parameters={
        "type": "object",
        "properties": {
            "daily": {
                "type": "array",
                "description": "Array of daily mentions, sentiment, top posts, and engagement for a brand.",
                "items": {
                    "type": "object",
                    "description": "Daily insights for a brand.",
                    "properties": {
                        "date": {
                            "type": "string",
                            "format": "date",
                            "description": "Date in ISO 8601 format (YYYY-MM-DD)."
                        },
                        "Topic": {
                            "type": "string",
                            "description": "Brand name."
                        },
                        "Mentions": {
                            "type": "number",
                            "description": "Total mentions of the Topic (brand) on the date."
                        },
                        "engagement": {
                            "type": "number",
                            "description": "Total engagement of the Topic (brand) on the date."
                        },
                        "sentiment_pos": {
                            "type": "number",
                            "description": "Positive sentiment mentions for the brand."
                        },
                        "sentiment_neu": {
                            "type": "number",
                            "description": "Neutral sentiment mentions for the brand."
                        },
                        "sentiment_neg": {
                            "type": "number",
                            "description": "Negative sentiment mentions for the brand."
                        },
                        "top_sites": {
                            "type": "array",
                            "description": "List of site names sorted by total mention in descending order.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "siteName": {
                                        "type": "string",
                                        "description": "Name of the site."
                                    },
                                    "mentions": {
                                        "type": "number",
                                        "description": "Total mentions on this site."
                                    },
                                    "sentiment_pos": {
                                        "type": "number",
                                        "description": "Positive sentiment mentions on this site."
                                    },
                                    "sentiment_neu": {
                                        "type": "number",
                                        "description": "Neutral sentiment mentions on this site."
                                    },
                                    "sentiment_neg": {
                                        "type": "number",
                                        "description": "Negative sentiment mentions on this site."
                                    }
                                }
                            }
                        },
                        "top_channels": {
                            "type": "array",
                            "description": "List of channels sorted by total mention in descending order.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "channelDeep": {
                                        "type": "string",
                                        "description": "Name of the channel."
                                    },
                                    "mentions": {
                                        "type": "number",
                                        "description": "Total mentions on this channel."
                                    },
                                    "sentiment_pos": {
                                        "type": "number",
                                        "description": "Positive sentiment mentions on this channel."
                                    },
                                    "sentiment_neu": {
                                        "type": "number",
                                        "description": "Neutral sentiment mentions on this channel."
                                    },
                                    "sentiment_neg": {
                                        "type": "number",
                                        "description": "Negative sentiment mentions on this channel."
                                    }
                                }
                            }
                        },
                        "top_posts": {
                            "type": "array",
                            "description": "Top posts (sorted by mention count or engagement).",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "parentId": {
                                        "type": "string",
                                        "description": "Unique identifier for the post."
                                    },
                                    "title": {
                                        "type": "string",
                                        "description": "Title of the post."
                                    },
                                    "engagement": {
                                        "type": "number",
                                        "description": "Engagement on the post."
                                    },
                                    "mentions": {
                                        "type": "number",
                                        "description": "Total mentions for the post."
                                    },
                                    "urlTopic": {
                                        "type": "string",
                                        "description": "URL of the post."
                                    },
                                    "sentiment_pos": {
                                        "type": "number",
                                        "description": "Positive sentiment mentions for the post."
                                    },
                                    "sentiment_neu": {
                                        "type": "number",
                                        "description": "Neutral sentiment mentions for the post."
                                    },
                                    "sentiment_neg": {
                                        "type": "number",
                                        "description": "Negative sentiment mentions for the post."
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
