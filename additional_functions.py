async def get_recent_history_until_negative(history):
    recent_history = []
    
    for record in reversed(history):
        recent_history.append(record)
        if record['amount'] < 0:
            break
    return recent_history