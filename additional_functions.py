from icecream import ic
async def get_recent_history_until_negative(history):
    recent_history = []
    
    for record in reversed(history):
        
        history_info = {

            'сумма': record['amount'],
            'дата': record['date']



        }




        recent_history.append(history_info)
        if record['amount'] < 0:
            break
    #print(recent_history[0])
    return recent_history