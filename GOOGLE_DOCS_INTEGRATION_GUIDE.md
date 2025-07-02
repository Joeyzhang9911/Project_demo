# SDG表单系统与Google Docs API集成完整指南

## 概述

本指南详细介绍如何将SDG表单系统与Google Docs API集成，实现实时共同编辑功能。集成后，用户可以：

1. **自动创建Google Docs文档**：当创建SDG表单时，系统自动在Google Docs中创建对应的文档
2. **实时同步内容**：表单内容变更时自动同步到Google Docs
3. **团队协作**：团队成员可以同时在Google Docs中编辑文档
4. **双向同步**：支持从Google Docs同步回表单系统
5. **实时协作**：通过WebSocket实现多用户实时编辑

---

## 认证方式对比

| 方式             | 适用场景         | 优点                | 缺点                |
|------------------|------------------|---------------------|---------------------|
| OAuth 2.0        | 本地开发/测试    | 易于调试，支持个人授权 | 需用户手动授权，token易失效 |
| Service Account  | 生产环境/自动化  | 无需用户交互，安全自动 | 需配置Drive权限，部分API有限制 |

---

## 1. Google Cloud Console 设置

### 1.1 创建项目
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google Docs API 和 Google Drive API

### 1.2 创建凭据
#### A. OAuth 2.0（开发/测试推荐）
1. "APIs & Services" > "Credentials" > "Create Credentials" > "OAuth 2.0 Client IDs"
2. 应用类型选 "Web application" 或 "Desktop application"
3. 添加重定向URI（如 `http://localhost:8000/auth/google/callback`）
4. 下载JSON凭据文件，重命名为 `credentials.json`，放在 `backend/app/` 目录

#### B. Service Account（生产推荐）
1. "IAM & Admin" > "Service Accounts" > "Create Service Account"
2. 选择 "Editor" 角色
3. 创建后进入 "Keys"，添加新密钥，选择JSON格式，下载后重命名为 `credentials.json`，放在 `backend/app/` 目录
4. （可选）如需将文档创建到特定文件夹，需将该文件夹共享给服务账号邮箱

### 1.3 配置OAuth同意屏幕
1. 配置应用信息，添加以下范围：
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/drive`

---

## 2. 环境变量配置

在 `.env` 文件中添加：
```env
# Google Docs API Configuration
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

---

## 3. Django与依赖配置

### 3.1 安装依赖
```bash
pip install google-api-python-client channels channels-redis
```

### 3.2 settings.py 关键配置
```python
INSTALLED_APPS += [
    'channels',
]
ASGI_APPLICATION = '_config.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379/0')],
        },
    },
}
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
```

---

## 4. 数据库迁移

```bash
python manage.py makemigrations sdg_action_plan
python manage.py migrate
```

---

## 5. 权限与安全
- 服务账号需有Google Docs/Drive编辑权限
- `credentials.json` 切勿提交到版本控制
- 定期轮换密钥，生产环境建议用环境变量管理敏感信息

---

## 6. 功能特性与API

### 6.1 自动文档创建与同步
- 创建/编辑SDG表单时自动同步Google Docs
- 支持团队成员自动共享文档
- 支持手动同步按钮

### 6.2 主要API端点
- `POST /api/sdg-action-plan/{id}/google-docs/`  同步/创建Google文档
- `GET /api/sdg-action-plan/{id}/google-docs/status/`  获取文档状态

### 6.3 前端集成要点
- 前端收到`auth_required`和`auth_url`时，弹窗跳转用户授权，授权后重试
- 支持WebSocket实时协作

---

## 7. 故障排查与常见问题

### 7.1 常见问题
- **认证错误**：检查凭据文件、OAuth同意屏幕、API是否启用
- **权限错误**：检查服务账号Drive权限、文档共享设置
- **WebSocket失败**：检查Redis服务、Channels配置、防火墙

### 7.2 调试建议
- 检查Django日志和Google Cloud Console API调用
- 使用文档中的调试代码片段定位问题

---

## 8. 最佳实践与性能
- 批量API操作、缓存机制、错误重试、监控告警
- 输入验证、访问控制、日志记录

---

## 9. 生产环境建议
- 推荐使用Service Account方式，凭据文件安全存储
- 环境变量管理敏感信息
- 配置HTTPS和CORS策略

---

## 10. 文件结构示例
```
backend/app/
├── credentials.json          # Google API凭据文件
├── token.pickle             # 自动生成的访问令牌（首次使用后创建）
├── manage.py
└── ...
```

---

## 11. 临时禁用Google Docs功能
- 前端隐藏Google Docs按钮
- 或注释后端相关代码

---

## 12. 参考与扩展阅读
- [Google Docs API 官方文档](https://developers.google.com/docs/api)
- [Google Drive API 官方文档](https://developers.google.com/drive)
- [Django Channels 官方文档](https://channels.readthedocs.io/)

---

**本指南合并自原有的GOOGLE_DOCS_INTEGRATION_GUIDE.md、backend/app/GOOGLE_DOCS_SETUP.md、backend/google_docs_setup.md，适用于SDG表单系统的Google Docs集成开发与部署。**