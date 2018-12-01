# cmsd
自定义基于select方法的循环式简单http服务器.


## 支持的功能
- 普通http请求
- http长连接
- URL参数列表
- websocket
- 扩展TCP通讯
- 兼容django渲染模板


## 使用http服务器
### 创建视图文件view.py
    import path
    from response import *
    from template import render
    from request import HttpRequest
    from httpd import TCPServerBasic

    @path.route(path='/', method=['GET'])
    def index(request):
        return render(request, "index.html")
 
    
    @path.route(path='/redir/', method=['GET'])
    def index(request):
        return HttpResponseRedirect("http://www.baidu.com")

    
    @path.route(path='/json/', method=['GET'])
    def index(request):
        return {'id': 1, "name": "cmsd"}
    
    
    @path.route(path='/print/<str:msg>/<int:id>', method=['GET', 'POST'])
    def index(request, msg, id):
        return msg + str(id)

    server = TCPServerBasic('127.0.0.1', 8000, HttpRequest)
    server.run_forever()

### 创建文件测试文件echo.py测试websocket
    import path
    from response import *
    from template import render
    from request import HttpRequest
    from httpd import TCPServerBasic

    class WebSocketEcho(HttpResponseWebSocket):
        def __init__(self, request):
            super().__init__(request)
        
        def on_text_frame(self, data):
            """
                called while receive a text frame
                return None
            """
            self.send_text(data)
        
        def on_bin_frame(self, data):
            """
                called while receive a binary frame
                return None
            """
            self.send_bin(data)
        
        def on_close_frame(self, data):
            """
                called while receive a close frame
                return None
            """
            self.close()
        
        def on_connection_down(self, request):
            """
                called while the connection is lost
                return None
            """
            print(request.path, "websocket is down.")
        

    @path.route(path='/live/', method=['GET'])
    def index(request):
        try:
            if request.headers['Upgrade'] != 'websocket':
                raise TypeError
            if request.headers['Connection'] != 'Upgrade':
                raise TypeError
        except:
            return HttpResponseBadRequest()
    
        return WebSocketEcho(request)


    server = TCPServerBasic('127.0.0.1', 8000, HttpRequest)
    server.run_forever()
    
#### js测试脚本
    var ws = new WebSocket("ws://localhost:8000/live/");
    ws.onopen = function(evt) {
        console.log("Connection open ...");
    };
    ws.onclose = function(evt){
        console.log("connection closed...")
    };
    ws.onmessage = function(evt) {
        console.log(evt.data)
    }

    ws.send(JSON.stringify({id:10, name:"杭州", close: true}))
    ws.close()
