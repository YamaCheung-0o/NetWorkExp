const http  = require('http');
const fs = require('fs').promises;
const path = require('path');

//建立服务器,这里使用异步避免在等待数据返回过程中整个界面冻住不能操作其他
const server = http.createServer(async(req, res) =>{
    // 打印请求信息
    console.log(`收到 ${req.method} 请求：${req.url}`);
    
    // 设置 CORS 头
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    // 处理 OPTIONS 请求（用于跨域预检）
    if (req.method === 'OPTIONS') {
        res.statusCode = 204;
        res.end();
        return;
    }
    
    let filePath;
    try{
        switch(req.url){
            case'/':
            filePath = path.join(__dirname,'public', 'example.html');
            //console.log(filePath);
            break;

            case'/about':
            filePath = path.join(__dirname,'public', 'about.html');
            break;

            case '/api/data':
                // API 接口，直接返回 JSON
                res.statusCode = 200;
                res.setHeader('Content-Type', 'application/json');
                res.end(JSON.stringify({
                    message: '这是来自服务器的 JSON 数据',
                    timestamp: Date.now()
                }));
                return;
            
            default:
                    // 尝试查找静态文件
                filePath = path.join(__dirname, 'public', req.url);

        }

        //读取文件内容
        const content = await fs.readFile(filePath, 'utf-8');
        //把扩展变量找出来
        const extname = path.extname(filePath);
        const contentType = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.svg': 'image/svg+xml'
        }[extname] || 'text/plain';//使用[extname]动态获取对应类型，如果找不到就默认为text/plain。
        
        // 返回文件内容
        res.statusCode = 200;
        res.setHeader('Content-Type', `${contentType}; charset=utf-8`);
        res.end(content);//返回用户"content"内容
            
    }
    catch(error){
         // 处理错误
         console.error(`错误处理请求 ${req.url}:`, error.message);
        
         if (error.code === 'ENOENT') {
             // 文件不存在，返回 404
             res.statusCode = 404;
             res.setHeader('Content-Type', 'text/html');
             //返回可以直接是html代码
             res.end(`
                 <html>
                 <body>
                     <h1>404 Not Found</h1>
                     <p>The Required Source is not exsisting: ${req.url}</p>
                 </body>
                 </html>
             `);
         } 
         else {
             // 其他错误，返回 500
             res.statusCode = 500;
             res.setHeader('Content-Type', 'text/plain');
             res.end(`服务器内部错误: ${error.message}`);
         }
     }
});


// 监听指定端口
const PORT = process.env.PORT || 3000;hg7
server.listen(PORT, () => {
    console.log(`✅ 服务器运行在 http://localhost:${PORT}`);
});

// 错误处理
server.on('error', (err) => {
    console.error(`❌ 服务器错误: ${err.message}`);
});  
