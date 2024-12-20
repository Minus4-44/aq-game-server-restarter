// Global variables
let currentGame = 'project_zomboid';
let currentController = null;
let projectZomboidServerEditor = null;
let projectZomboidSandboxEditor = null;
let palworldConfigEditor = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Project Zomboid editors
    projectZomboidServerEditor = CodeMirror.fromTextArea(document.getElementById('server-config-editor'), {
        mode: 'properties',
        theme: 'monokai',
        lineNumbers: true,
        matchBrackets: true,
        indentUnit: 4,
        lineWrapping: true
    });

    projectZomboidSandboxEditor = CodeMirror.fromTextArea(document.getElementById('sandbox-config-editor'), {
        mode: 'properties',
        theme: 'monokai',
        lineNumbers: true,
        matchBrackets: true,
        indentUnit: 4,
        lineWrapping: true
    });

    // Initialize Palworld editor
    palworldConfigEditor = CodeMirror.fromTextArea(document.getElementById('palworld-config-editor'), {
        mode: 'properties',
        theme: 'monokai',
        lineNumbers: false,
        matchBrackets: true,
        indentUnit: 4,
        lineWrapping: true
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
    const projectZomboidEditors = document.getElementById('project-zomboid-editors');
    const palworldEditor = document.getElementById('palworld-editor');
    
    // Hide all editors first
    forceRestartBtn.style.display = 'none';
    if (projectZomboidEditors) projectZomboidEditors.style.display = 'none';
    if (palworldEditor) palworldEditor.style.display = 'none';

    // Show relevant editors
    if (game === 'project_zomboid') {
        forceRestartBtn.style.display = 'block';
        if (projectZomboidEditors) {
            projectZomboidEditors.style.display = 'grid';
            loadConfig('project_zomboid', 'server');
            loadConfig('project_zomboid', 'sandbox');
        }
    } else if (game === 'palworld') {
        if (palworldEditor) {
            palworldEditor.style.display = 'grid';
            loadPalworldConfig();
        }
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

// Project Zomboid Configuration
async function loadConfig(serverType, configType) {
    try {
        const endpoint = configType === 'server' 
            ? '/project_zomboid/get_server_config'
            : '/project_zomboid/get_sandbox_config';
            
        const response = await fetch(endpoint);
        const data = await response.json();
        
        if (response.ok && data.content) {
            if (configType === 'server') {
                projectZomboidServerEditor.setValue(data.content);
            } else {
                projectZomboidSandboxEditor.setValue(data.content);
            }
            showToast('Configuration loaded successfully');
        } else {
            showToast('Failed to load configuration file', 5000);
        }
    } catch (error) {
        showToast(`Load failed: ${error.message}`, 5000);
    }
}

async function saveConfig(serverType, configType) {
    try {
        const endpoint = configType === 'server'
            ? '/project_zomboid/override_server_config'
            : '/project_zomboid/override_sandbox_config';

        const content = configType === 'server' 
            ? projectZomboidServerEditor.getValue()
            : projectZomboidSandboxEditor.getValue();
            
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

// Palworld Configuration
async function loadPalworldConfig() {
    try {
        console.log('Fetching Palworld config...');
        const response = await fetch('/palworld/get_config', {
            headers: {
                'Accept': 'application/json'
            }
        });
        console.log('Response received:', response);
        const responseText = await response.text();
        console.log('Raw response text:', responseText);
        
        // Try to parse the response as JSON
        let data;
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            // If parsing fails, wrap the raw text in a JSON structure
            data = {
                status: 'success',
                content: responseText
            };
        }
        
        if (data.status === 'success') {
            palworldConfigEditor.setValue(data.content);
            showToast('Configuration loaded successfully');
        } else {
            showToast(data.message || 'Failed to load configuration file', 5000);
        }
    } catch (error) {
        console.error('Load error:', error);
        showToast(`Load failed: ${error.message}`, 5000);
    }
}

async function savePalworldConfig() {
    try {
        const content = palworldConfigEditor.getValue();
        const blob = new Blob([content], { type: 'text/plain' });
        const formData = new FormData();
        formData.append('file', blob, 'PalWorldSettings.ini');
        
        const response = await fetch('/palworld/override_config', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        showToast(data.message || (response.ok ? 'Configuration saved successfully' : 'Save failed'));
    } catch (error) {
        showToast(`Save failed: ${error.message}`, 5000);
    }
}
