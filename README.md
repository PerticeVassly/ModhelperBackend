# 项目目的

ModHelper是一个基于LLM的我的世界（MC）模组助手系统，旨在帮助玩家理解、检索和使用各类游戏模组信息。后端系统提供了知识检索、模组推荐和问答功能，为用户提供沉浸式的模组知识体验。

# 使用的框架和技术

核心技术栈

* FastAPI: 高性能Python Web框架，用于构建API端点
* LLM集成: 支持DeepSeek等大型语言模型接口
* RAG技术: 实现检索增强生成，提高回答准确性

数据存储

* MongoDB: 存储用户信息、对话历史和消息数据
* Neo4j: 图数据库，用于存储模组之间的关系
* ChromaDB: 向量数据库，用于相似度搜索
* SQLite: 轻量级数据库，存储模组元数据

其他技术

* 百度向量嵌入API: 用于文本向量化
* 异步处理: 使用Python asyncio处理并发请求

# 部署方式

## 服务器访问

http://172.29.4.206/

## 后端本地运行方法

### 1. 创建虚拟环境并且安装依赖

```bash
python -m venv .venv  
```
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```

后续的操作保持在此虚拟环境下

### 2. 准备数据库

其中`chroma`和`sqlite3`是文件数据库，会自动创建。

需要安装`MongoDB`和`Neo4j`数据库。（Ubuntu22.04）

可以参考其他教程, 或者直接问GPT，以下只是一种参考

**MongoDB安装**

获取MongoDB的公钥

```bash
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
```

添加MongoDB源

```bash
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

apt更新，安装

```bash
sudo apt update
sudo apt install -y mongodb-org
```

启动并且设置开机自启（第二条是开机自启，可选）

```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

使用mongosh，mongodb默认没有密码，应该可以直接连接成功

```bash
mongosh
```

**neo4j安装**

获取Neo4j的公钥

```bash
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/neo4j.gpg
```

添加Neo4j源

```bash
echo "deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable 5" | sudo tee /etc/apt/sources.list.d/neo4j.list
```

apt更新，安装

```bash
sudo apt update
sudo apt install -y neo4j
```

启动并且设置开机自启（第二条是开机自启，可选）

```bash
sudo systemctl enable neo4j
sudo systemctl start neo4j
```

默认账号密码是 `neo4j` / `neo4j`，首次登录会强制修改密码。

使用`cypher-shell`登入

```bash
cypher-shell -u neo4j  
```

### 3. API准备

`LLM_API_KEY`在以下网站创建

https://platform.deepseek.com/api_keys

`EMBEDDING_API_KEY`在以下网站创建

https://console.bce.baidu.com/iam/#/iam/apikey/list

复制`.env.template`，重命名为`.env`，并且修改里面的配置

填入上述两个apikey,以及neo4j的数据库密码

### 4. 数据准备

根目录下创建一个/data/raw文件夹

复制Crawler项目中/data中的所有`*new.json`文件，到`/data/raw`下。（`*new.json`是一个demo数据）

运行导入数据脚本, 参数为要导入的数据的后缀（此处为`new`）

```bash
python scripts/load_data.py new 
```

### 5. 启动后端

```bash
python main.py
```
