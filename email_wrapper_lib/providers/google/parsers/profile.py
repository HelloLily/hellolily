

def parse_profile(data, promise=None):
    profile = {
        'user_id': data['emailAddress'],
        'username': data['emailAddress'],
        'history_id': data['historyId'],
        'messages_count': data['messagesTotal'],
        'threads_count': data['threadsTotal'],
    }

    if promise:
        promise.resolve(profile)

    return profile
