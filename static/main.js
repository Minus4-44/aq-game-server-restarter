// 初始化编辑器
let serverConfigEditor = CodeMirror.fromTextArea(document.getElementById('server-config-editor'), {
    mode: 'properties',
    theme: 'monokai',
    lineNumbers: true,
    autoCloseBrackets: true,
    matchBrackets: true,
    indentUnit: 4,
    lineWrapping: true,
});

let sandboxConfigEditor = CodeMirror.fromTextArea(document.getElementById('sandbox-config-editor'), {
    mode: 'lua',
    theme: 'monokai',
    lineNumbers: true,
    autoCloseBrackets: true,
    matchBrackets: true,
    indentUnit: 4,
    lineWrapping: true,
});

// 游戏切换功能
function switchGame(gameName) {
    // 更新选择器按钮状态
    document.querySelectorAll('.game-selector-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-game="${gameName}"]`).classList.add('active');

    // 更新面板显示
    document.querySelectorAll('.game-panel').forEach(panel => {
        panel.classList.remove('active');
        panel.classList.add('hidden');
    });
    const targetPanel = document.getElementById(`${gameName}-panel`);
    targetPanel.classList.remove('hidden');
    targetPanel.classList.add('active');

    // 如果切换到Project Zomboid，加载配置
    if (gameName === 'project_zomboid') {
        loadConfig('project_zomboid', 'server');
        loadConfig('project_zomboid', 'sandbox');
    }
}

// 显示提示消息
function showToast(message, duration = 3000) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    toastMessage.textContent = message;
    toast.classList.remove('hiding');
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => {
            toast.classList.add('hidden');
            toast.classList.remove('hiding');
        }, 300);
    }, duration);
}

// 重启服务器
async function restartServer(serverType, forceDelete = false) {
    try {
        const endpoint = serverType === 'project_zomboid' 
            ? `/project_zomboid/restart${forceDelete ? '?force_delete_saves=true' : ''}`
            : `/${serverType}/restart`;
            
        const response = await fetch(endpoint, {
            method: 'POST'
        });
        
        const data = await response.json();
        showToast(`${serverType} 服务器重启${response.ok ? '成功' : '失败'}`);
    } catch (error) {
        showToast(`重启失败: ${error.message}`, 5000);
    }
}

// 加载配置
async function loadConfig(serverType, configType) {
    try {
        let endpoint = '';
        if (serverType === 'project_zomboid') {
            endpoint = configType === 'server' 
                ? '/project_zomboid/get_server_config'
                : '/project_zomboid/get_sandbox_config';
        }
            
        const response = await fetch(endpoint);
        const data = await response.json();
        
        if (response.ok && data.content) {
            if (configType === 'server') {
                serverConfigEditor.setValue(data.content);
            } else {
                sandboxConfigEditor.setValue(data.content);
            }
            showToast('配置加载成功');
        } else {
            showToast('获取配置文件失败', 5000);
        }
    } catch (error) {
        showToast(`加载失败: ${error.message}`, 5000);
    }
}

// 保存配置
async function saveConfig(serverType, configType) {
    try {
        let endpoint = '';
        if (serverType === 'project_zomboid') {
            endpoint = configType === 'server'
                ? '/project_zomboid/override_server_config'
                : '/project_zomboid/override_sandbox_config';
        }

        const content = configType === 'server' 
            ? serverConfigEditor.getValue()
            : sandboxConfigEditor.getValue();
            
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        });
        
        const data = await response.json();
        showToast(`配置${response.ok ? '保存成功' : '保存失败'}`);
    } catch (error) {
        showToast(`保存失败: ${error.message}`, 5000);
    }
}

// 获取配置文件
async function getConfig(serverType, configType) {
    try {
        let endpoint = '';
        if (serverType === 'project_zomboid') {
            endpoint = configType === 'server' 
                ? '/project_zomboid/get_server_config'
                : '/project_zomboid/get_sandbox_config';
        }
            
        const response = await fetch(endpoint);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = configType === 'server' ? 'server-config.ini' : 'sandbox-config.ini';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showToast('配置文件下载成功');
        } else {
            showToast('获取配置文件失败', 5000);
        }
    } catch (error) {
        showToast(`获取配置失败: ${error.message}`, 5000);
    }
}

// 上传配置文件
async function uploadConfig(serverType, configType, file) {
    if (!file) return;

    const formData = new FormData();
    formData.append('config', file);

    try {
        let endpoint = '';
        if (serverType === 'project_zomboid') {
            endpoint = configType === 'server'
                ? '/project_zomboid/override_server_config'
                : '/project_zomboid/override_sandbox_config';
        }
            
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        showToast(`配置文件上传${response.ok ? '成功' : '失败'}`);
    } catch (error) {
        showToast(`上传失败: ${error.message}`, 5000);
    }
}

// 初始加载配置
document.addEventListener('DOMContentLoaded', () => {
    loadConfig('project_zomboid', 'server');
    loadConfig('project_zomboid', 'sandbox');
});
