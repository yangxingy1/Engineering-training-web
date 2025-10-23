# frontend/Dockerfile

# 1. 使用官方的 Nginx 轻量级镜像 (alpine 版本非常小)
FROM nginx:stable-alpine

# 2. 将你本地的静态文件 (html, css, js, lib, image) 
#    复制到 Nginx 容器内用于托管网站的默认目录中
COPY . /usr/share/nginx/html

# 3. 将我们刚刚编写的 nginx.conf 配置文件
#    复制到容器内 Nginx 的默认配置目录中，覆盖掉它原来的配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 4. 暴露容器的 80 端口
EXPOSE 80

# 5. 容器启动时执行的命令 (启动 Nginx 服务)
CMD ["nginx", "-g", "daemon off;"]