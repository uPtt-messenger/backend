import datetime


class PTTChatMessage:
    username: str
    message: str
    date: str

    def __init__(self, username: str, message: str, date: str):
        self.username = username

        message = message[:message.find('====================')].strip()
        self.message = message

        # convert Sun Apr 21 10:59:24 2024 to 2024-04-21 10:59:24
        date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S %Y')
        self.date = date.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            'username': self.username,
            'message': self.message,
            'date': self.date}
