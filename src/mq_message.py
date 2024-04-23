import datetime
import json


class Message:
    channel: str
    reply_channel: str
    message: str

    def __init__(self, channel: str, reply_channel: str, message: dict):
        self.channel = channel
        self.reply_channel = reply_channel

        message['reply_channel'] = reply_channel
        self.message = json.dumps(message)

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            'channel': self.channel,
            'message': self.message}


class CloseMessage(Message):
    def __init__(self, channel: str, reply_channel: str):
        super().__init__(
            channel,
            reply_channel,
            {
                'category': 'close'})


class SelfCloseMessage(Message):
    def __init__(self, channel: str, reply_channel: str):
        super().__init__(
            channel,
            reply_channel,
            {
                'category': 'self_close'})


class StatusMessage(Message):
    state: str

    def __init__(self, channel: str, reply_channel: str, action: str, state: str, message: str = None):
        super().__init__(
            channel,
            reply_channel,
            {
                'category': 'status',
                'action': action,
                'state': state,
                'message': message})


class LoginMessage(Message):
    username: str
    password: str

    def __init__(self, channel: str, reply_channel: str, username: str, password: str):
        super().__init__(
            channel,
            reply_channel,
            {
                'category': 'login',
                'username': username,
                'password': password})


class LogoutMessage(Message):
    def __init__(self, channel: str, reply_channel: str):
        super().__init__(
            channel,
            reply_channel,
            {
                'category': 'logout'})


class SendChatMessage(Message):
    """
    Chat message to be sent through PTT
    """

    username: str
    message: str

    def __init__(self, channel: str, reply_channel: str, username: str, message: str):
        content = '\r\n'.join([
            message,
            '=' * 20,
            '',
            '有人在 uPtt 上跟你說話！',
            'uPtt 是一款專為 Ptt 設計的跨平台即時通訊軟體，支援 Mac 與 Windows 作業系統',
            '可以讓您在電腦上方便地收發 Ptt 訊息，不必再額外登入。',
            'uPtt 透過 Ptt 官方伺服器進行登入驗證,確保帳號安全無虞。訊息傳遞也是建立在 Ptt 現有架構上，完整相容原有的訊息功能。',
            '官方網站: https://qqqqqq',
        ])

        super().__init__(
            channel,
            reply_channel,
            {
                'category': 'send_chat',
                'username': username,
                'message': content})


class RecvChatMessage(Message):
    """
    Chat message received from PTT
    """

    username: str
    date: str
    message: str

    def __init__(self, channel: str, reply_channel: str, username: str, date: str, message: str):
        message = message[:message.find('====================')].strip()
        self.chat_content = message

        # convert Sun Apr 21 10:59:24 2024 to 2024-04-21 10:59:24
        date = datetime.datetime.strptime(date, '%a %b %d %H:%M:%S %Y')
        date = date.strftime('%Y-%m-%d %H:%M:%S')

        super().__init__(
            channel,
            reply_channel,
            {
                'category': 'recv_chat',
                'username': username,
                'date': date,
                'message': message})
