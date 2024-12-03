import pusher

class PusherClient:
    def __init__(self):
        self.pusher_client = pusher.Pusher(
        app_id='1905229',
        key='c2af53527e653bf225b9',
        secret='88c71a5411ff67f24929',
        cluster='mt1',
        ssl=True
    )

    def notificar(self, canal, evento, data):
        self.pusher_client.trigger(canal, evento, data)