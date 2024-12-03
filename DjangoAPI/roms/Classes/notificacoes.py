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

    def notificarLike(self, username, content_nome, id_user, id_content):
        self.pusher_client.trigger('like-channel', 'like-event', {'message': f'{username} deu like no seu {content_nome}',
                                                                  'id_user': id_user,
                                                                  'id_content': id_content,
                                                                  'username': username, 
                                                                  'content_nome': content_nome})