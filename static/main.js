// Global variables
let currentGame = 'project_zomboid';
let currentController = null;
let serverConfigEditor = null;
let sandboxConfigEditor = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize editors
    serverConfigEditor = CodeMirror.fromTextArea(document.getElementById('server-config-editor'), {
        mode: 'properties',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        lineWrapping: true,
    });

    sandboxConfigEditor = CodeMirror.fromTextArea(document.getElementById('sandbox-config-editor'), {
        mode: 'lua',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        lineWrapping: true,
    });

    // Set initial game
    setCurrentGame(window.location.pathname.substring(1) || 'project_zomboid');

    // Add navigation event listeners
    document.querySelectorAll('nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const game = link.getAttribute('data-game');
            setCurrentGame(game);
            window.history.pushState({game}, '', `/${game}`);
        });
    });
});

// Set current game
function setCurrentGame(game) {
    currentGame = game;
    
    // Update navigation state
    document.querySelectorAll('nav a').forEach(link => {
        link.classList.remove('bg-gray-700');
        if (link.getAttribute('data-game') === game) {
            link.classList.add('bg-gray-700');
        }
    });

    // Update title
    const titles = {
        'project_zomboid': 'Project Zomboid Server Management',
        'satisfactory': 'Satisfactory Server Management',
        'palworld': 'PalWorld Server Management'
    };
    document.querySelector('.game-title').textContent = titles[game];

    // Update UI elements
    const forceRestartBtn = document.getElementById('force-restart-btn');
    const configEditors = document.getElementById('config-editors');
    
    if (game === 'project_zomboid') {
        forceRestartBtn.style.display = '';
        configEditors.style.display = '';
        loadConfig(game, 'server');
        loadConfig(game, 'sandbox');
    } else {
        forceRestartBtn.style.display = 'none';
        configEditors.style.display = 'none';
    }

    // Clear command output
    clearOutput();
}

// Command output handling
function getOutputPre() {
    return document.querySelector('.bg-gray-900 pre');
}

function appendOutput(text) {
    const outputPre = getOutputPre();
    if (outputPre) {
        outputPre.textContent += text;
        outputPre.scrollTop = outputPre.scrollHeight;
    }
}

function clearOutput() {
    const outputPre = getOutputPre();
    if (outputPre) {
        outputPre.textContent = '';
    }
}

// Show toast message
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

// Restart server
async function restartServer(serverType, forceDelete = false) {
    try {
        if (currentController) {
            currentController.abort();
        }

        currentController = new AbortController();
        
        const endpoint = serverType === 'project_zomboid' 
            ? `/project_zomboid/restart${forceDelete ? '?force_delete_saves=true' : ''}`
            : `/${serverType}/restart`;
            
        clearOutput();
        appendOutput(`Restarting ${serverType} server...\n`);

        const response = await fetch(endpoint, {
            method: 'POST',
            signal: currentController.signal
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        try {
            while (true) {
                const {value, done} = await reader.read();
                if (done) break;
                
                let text;
                try {
                    text = decoder.decode(value, {stream: true});
                } catch (e) {
                    // If UTF-8 decoding fails, try using GBK
                    const gbkDecoder = new TextDecoder('gbk');
                    text = gbkDecoder.decode(value);
                }
                appendOutput(text);
            }
        } catch (error) {
            appendOutput(`\nDecoding error: ${error.message}\n`);
        }

        showToast(`${serverType} server restart completed`);
    } catch (error) {
        if (error.name === 'AbortError') {
            appendOutput('\nOperation cancelled\n');
        } else {
            appendOutput(`\nError: ${error.message}\n`);
            showToast(`Restart failed: ${error.message}`, 5000);
        }
    } finally {
        currentController = null;
    }
}

// Load configuration
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
            showToast('Configuration loaded successfully');
        } else {
            showToast('Failed to load configuration file', 5000);
        }
    } catch (error) {
        showToast(`Load failed: ${error.message}`, 5000);
    }
}

// Save configuration
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
        showToast(`Configuration ${response.ok ? 'saved successfully' : 'save failed'}`);
    } catch (error) {
        showToast(`Save failed: ${error.message}`, 5000);
    }
}
