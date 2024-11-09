<script>
    import { onMount, onDestroy } from 'svelte';
    import { Download, File, MoveHorizontal } from 'lucide-svelte';
    
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
        ws = new WebSocket('ws://localhost:8000/ws/monitor');
        
        ws.onopen = () => {
            connectionStatus = 'Connected';
            console.log('WebSocket connected');
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (!data.metadata) {
                data.metadata = {
                    name: '',
                    extension: '',
                    size: 0,
                    created: '',
                    modified: '',
                    path: '',
                    is_hidden: false
                };
            }
            messages = [data, ...messages].slice(0, 100);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            connectionStatus = 'Error';
        };

        ws.onclose = () => {
            connectionStatus = 'Disconnected';
            setTimeout(connectWebSocket, 3000);
        };
    }

    onMount(() => {
        connectWebSocket();
    });

    onDestroy(() => {
        if (ws) ws.close();
    });
</script>

<main class="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-6">
    <!-- 연결 상태 표시 -->
    <div class="px-3 py-1 rounded-full text-sm font-medium inline-flex w-fit {
        connectionStatus === 'Connected' ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300' :
        connectionStatus === 'Error' ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300' :
        'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300'
    }">
        {connectionStatus}
    </div>

    <div class="grid gap-2">
        {#each messages as message}
            <div class="flex items-center gap-4 rounded-lg p-3 transition-colors {
                message.type === 'created' ? 'bg-green-50 dark:bg-green-900/20' :
                message.type === 'modified' ? 'bg-yellow-50 dark:bg-yellow-900/20' :
                'bg-red-50 dark:bg-red-900/20'
            }">
                <File class="h-8 w-8 {
                    message.type === 'created' ? 'text-green-600 dark:text-green-400' :
                    message.type === 'modified' ? 'text-yellow-600 dark:text-yellow-400' :
                    'text-red-600 dark:text-red-400'
                }" />
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                        <span class="text-sm font-medium">{message.metadata.name}</span>
                        <span class="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-800">
                            {message.metadata.extension}
                        </span>
                        {#if message.metadata.is_hidden}
                            <span class="px-2 py-1 text-xs rounded-full bg-gray-600 text-white">숨김</span>
                        {/if}
                    </div>
                    <div class="grid grid-cols-3 gap-2 mt-1 text-sm text-gray-500 dark:text-gray-400">
                        <span>크기: {formatSize(message.metadata.size)}</span>
                        <span>생성: {message.metadata.created}</span>
                        <span>수정: {message.metadata.modified}</span>
                    </div>
                    <div class="mt-1 text-xs text-gray-400 dark:text-gray-500 truncate">
                        {message.metadata.path}
                    </div>
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">
                    {formatDate(message.timestamp)}
                </div>
                <div class="flex items-center gap-2">
                    <button class="p-2 rounded-lg" aria-label="Download">
                        <Download class="h-4 w-4" />
                    </button>
                    <button class="p-2 rounded-lg" aria-label="More options">
                        <MoveHorizontal class="h-4 w-4" />
                    </button>
                </div>
            </div>
        {/each}
    </div>
</main>