def generate_choice_1_content(previous:str, related:str, query:str):
    content_prompt = f"""
    Recent Messages:
    {previous}

    Related Messages:
    {related}

    User Query:
    {query}

    Now respond as GrexAI, a teammate in the group chat.
    """

    return content_prompt