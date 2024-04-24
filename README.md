## k8s Image Replacer Admission Webhook
在国内部署开源服务时镜像下载失败一直是个让人头疼的问题，本来一键就能安装运行的服务
现在得分好几步来操作:
- 1、特定的代理机器来完成镜像下载
- 2、推送到内部仓库
- 3、修改yaml文件/helm的values，使用内部仓库的镜像  
后续需要更新镜像时还得重复上述步骤，甚是麻烦，浪费宝贵的时间。

本工具利用k8s的Admission Webhook机制，自动对容器镜像进行替换, 默认使用国内的`m.daocloud.com`镜像缓存源来加速镜像下载  
替换规则如下：
```
redis => m.daocloud.com/docker.io/library/redis
nginx/nginx => m.daocloud.com/docker.io/nginx/nginx
quay.io/nginx/nginx => m.daocloud.com/quay.io/nginx/nginx
```

## 安装
```
make k8s-deploy
```

## 卸载
```
make k8s-delete-all
```

## 特别鸣谢
- [DaoCloud Public Image Mirror](https://github.com/DaoCloud/public-image-mirror)