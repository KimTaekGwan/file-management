<script>
    import { onMount, onDestroy } from 'svelte';
    let messages = [];
    let ws;
    let connectionStatus = 'Disconnected';

    function formatSize(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 Byte';
        const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
    }

    function formatDate(timestamp) {
        return new Date(timestamp * 1000).toLocaleString();
    }

    function connectWebSocket() {
        ws = new WebSocket('ws://localhost:8000/monitor/ws');
        
        ws.onopen = () => {
            connectionStatus = 'Connected';
            console.log('WebSocket connected');
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);
            messages = [data, ...messages].slice(0, 100);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            connectionStatus = 'Error';
        };

        ws.onclose = () => {
            connectionStatus = 'Disconnected';
            setTimeout(connectWebSocket, 3000); // 재연결 시도
        };
    }

    onMount(() => {
        connectWebSocket();
    });

    onDestroy(() => {
        if (ws) ws.close();
    });
</script>

<div class="container">
    <h1>File Monitor</h1>
    <div class="status {connectionStatus.toLowerCase()}">{connectionStatus}</div>
    <div class="messages">
        {#each messages as message}
            <div class="message {message.type}">
                <div class="event-type">{message.type}</div>
                <div class="file-info">
                    <h3>
                        {message.metadata.name}
                        <span class="extension">{message.metadata.extension}</span>
                        {#if message.metadata.is_hidden}
                            <span class="hidden-badge">숨김</span>
                        {/if}
                    </h3>
                    <div class="metadata">
                        <span>크기: {formatSize(message.metadata.size)}</span>
                        <span>생성: {message.metadata.created}</span>
                        <span>수정: {message.metadata.modified}</span>
                    </div>
                    <div class="path">{message.metadata.path}</div>
                </div>
                <div class="timestamp">{formatDate(message.timestamp)}</div>
            </div>
        {/each}
    </div>
</div>

<style>
    .extension {
        font-size: 0.8em;
        color: #666;
        background: #eee;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 8px;
    }

    .metadata {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #666;
    }

    .metadata span {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .status {
        padding: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
        border-radius: 4px;
    }

    .status.connected { background-color: #e6ffe6; color: #006600; }
    .status.disconnected { background-color: #ffe6e6; color: #660000; }
    .status.error { background-color: #ffebcc; color: #663300; }
    .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }

    .messages {
        max-height: 600px;
        overflow-y: auto;
        border: 1px solid #ccc;
        border-radius: 4px;
    }

    .message {
        padding: 1rem;
        border-bottom: 1px solid #eee;
        display: grid;
        grid-template-columns: 100px 1fr 150px;
        gap: 1rem;
        align-items: center;
    }

    .created { background-color: #e6ffe6; }
    .modified { background-color: #fff5e6; }
    .deleted { background-color: #ffe6e6; }

    .event-type {
        text-transform: uppercase;
        font-weight: bold;
    }

    .file-info {
        overflow: hidden;
    }

    .file-info h3 {
        margin: 0;
        font-size: 1.1rem;
    }

    .metadata {
        display: flex;
        gap: 1rem;
        font-size: 0.9rem;
        color: #666;
        margin: 0.5rem 0;
    }

    .path {
        font-size: 0.8rem;
        color: #999;
        word-break: break-all;
    }

    .timestamp {
        font-size: 0.8rem;
        color: #666;
    }
    
    .hidden-badge {
        font-size: 0.7em;
        background: #666;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 8px;
        vertical-align: middle;
    }
</style>