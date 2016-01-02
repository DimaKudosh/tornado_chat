import tornado.ioloop
import tornado.web
import tornado.websocket
import tornadoredis
import tornado.gen
import os
import json


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html", title="Tornado tutorial")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/messages/', MessageWebSocket),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        super().__init__(handlers, **settings)
        self.client = tornadoredis.Client()
        self.client.connect()
        self.client.publish('chat', 'Main Chat')


class MessageWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MessageWebSocket, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, 'chat')
        self.client.listen(self.on_redis_message)

    def on_message(self, msg):
        self.application.client.publish('chat', json.dumps(msg))

    def on_redis_message(self, msg):
        if msg.kind == 'message':
            self.write_message(str(msg.body))
        if msg.kind == 'disconnect':
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe('chat')
            self.client.disconnect()


if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    print("Tornado is working on localhost:8888")
    tornado.ioloop.IOLoop.current().start()
