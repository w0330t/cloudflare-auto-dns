# Cloudflare Auto DNS

> 针对 Adguard Home 对 Cloudflare 的站点网络优化。

本程序将调用 [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest) 自动解析 Cloudflare 的最优质的IP解析并将其写入 Adguard Home 的 DNS 覆写，以便在访问指定网站或者服务的时候获得更加良好的体验。

## 使用指南

### 项目使用条件

本项目可以直接运行Python文件或者使用docker部署。

虽然理论上是全平台。但本项目仅在Linux上调试运行。

#### 使用`docker-compose`部署

1. 克隆本项目

```shell
git clone https://github.com/w0330t/cloudflare-auto-dns.git
```

2. 进入克隆的目录中，将`config-example.toml`文件复制然后重命名为`config.toml`，根据自己的需求修改内容。

3. 安装好docker-compose后，直接执行下面的命令即可。

```shell
docker-compose up -d
```

#### 手动运行

1. 克隆本项目

```shell
git clone https://github.com/w0330t/cloudflare-auto-dns.git
```

2. 进入克隆的目录中，将`config-example.toml`文件复制然后重命名为`config.toml`，根据自己的需求修改内容。

3. 下载 [CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest) 的最新版本并解压缩到`CloudflareSpeedTest`文件夹中，此时大概目录长这样
```
.
├── CloudflareSpeedTest
│   ├── 使用+错误+反馈说明.txt
│   ├── cfst_hosts.sh
│   ├── CloudflareST
│   ├── ip.txt
│   └── ipv6.txt
├── config-example.toml
├── config.toml
├── docker-compose.yml
├── Dockerfile
├── main.py
├── readme.md
└── requirements.txt
```

4. 使用pip安装依赖

```shell
pip install --no-cache-dir -r requirements.txt
```

5. 直接开始运行

```shell
python main.py
```


## 授权协议

The GPL-3.0 License.