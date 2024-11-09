<script>
    import { onMount, onDestroy } from 'svelte';
    import TreeNode from '$lib/components/TreeNode.svelte';
    import { Folder, File, RefreshCw } from 'lucide-svelte';
    
    let fileTree = null;
    let expandedNodes = new Set();
    let searchQuery = '';
    let searchResults = [];
    let ws;
    let connectionStatus = 'Disconnected';

    async function fetchFileTree() {
        try {
            const response = await fetch('http://localhost:8000/api/filesystem/tree');
            fileTree = await response.json();
            console.log('파일 트리 새로고침 완료');
        } catch (error) {
            console.error('파일 트리 가져오기 실패:', error);
        }
    }

    function addNodeToTree(tree, newNode) {
        const parentPath = newNode.path.substring(0, newNode.path.lastIndexOf('/'));
        const parent = findNodeByPath(tree, parentPath);
        
        if (parent) {
            if (!parent.children) parent.children = [];
            parent.children = [...parent.children, newNode];
            parent.children.sort((a, b) => a.name.localeCompare(b.name));
            fileTree = {...fileTree};
        }
    }

    function updateNodeInTree(tree, updatedNode) {
        const node = findNodeByUuid(tree, updatedNode.uuid);
        if (node) {
            Object.assign(node, updatedNode);
            fileTree = {...fileTree};
        }
    }

    function removeNodeFromTree(tree, removeNode) {
        const parent = findParentNode(tree, removeNode.uuid);
        if (parent && parent.children) {
            parent.children = parent.children.filter(child => child.uuid !== removeNode.uuid);
            fileTree = {...fileTree};
        }
    }

    function findNodeByPath(tree, path) {
        if (tree.path === path) return tree;
        if (!tree.children) return null;
        
        for (const child of tree.children) {
            const found = findNodeByPath(child, path);
            if (found) return found;
        }
        return null;
    }

    function findNodeByUuid(tree, uuid) {
        if (tree.uuid === uuid) return tree;
        if (!tree.children) return null;
        
        for (const child of tree.children) {
            const found = findNodeByUuid(child, uuid);
            if (found) return found;
        }
        return null;
    }

    function findParentNode(tree, uuid, parent = null) {
        if (tree.uuid === uuid) return parent;
        if (!tree.children) return null;
        
        for (const child of tree.children) {
            const found = findParentNode(child, uuid, tree);
            if (found) return found;
        }
        return null;
    }

    function connectWebSocket() {
        ws = new WebSocket('ws://localhost:8000/ws/filesystem');
        
        ws.onopen = () => {
            connectionStatus = 'Connected';
            console.log('WebSocket 연결됨');
            // 초기 트리 데이터 요청
            ws.send(JSON.stringify({ action: 'get_tree' }));
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('수신된 메시지:', data);
            
            if (data.type === 'filesystem_tree') {
                fileTree = data.data;
            } else if (data.type === 'created') {
                // 새로운 노드를 트리에 추가하는 로직
                addNodeToTree(fileTree, data.node);
            } else if (data.type === 'modified') {
                // 기존 노드 정보 업데이트 로직
                updateNodeInTree(fileTree, data.node);
            } else if (data.type === 'deleted') {
                // 노드를 트리에서 제거하는 로직
                removeNodeFromTree(fileTree, data.node);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket 오류:', error);
            connectionStatus = 'Error';
        };

        ws.onclose = () => {
            connectionStatus = 'Disconnected';
            setTimeout(connectWebSocket, 3000); // 재연결 시도
        };
    }

    async function searchFiles() {
        if (!searchQuery.trim()) {
            searchResults = [];
            return;
        }
        const response = await fetch(`http://localhost:8000/api/filesystem/search?query=${searchQuery}`);
        searchResults = await response.json();
    }

    function toggleNode(uuid) {
        if (expandedNodes.has(uuid)) {
            expandedNodes.delete(uuid);
        } else {
            expandedNodes.add(uuid);
        }
        expandedNodes = expandedNodes;
    }

    onMount(() => {
        connectWebSocket();
    });

    onDestroy(() => {
        if (ws) ws.close();
    });
</script>

<div class="container mx-auto p-4">
    <div class="flex gap-4">
        <div class="w-1/3 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div class="mb-4 flex justify-between items-center">
                <h2 class="text-lg font-semibold">파일 시스템</h2>
                <div class="flex items-center gap-2">
                    <span class="text-sm {
                        connectionStatus === 'Connected' ? 'text-green-500' :
                        connectionStatus === 'Error' ? 'text-red-500' :
                        'text-yellow-500'
                    }">
                        {connectionStatus}
                    </span>
                    <button
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                        on:click={fetchFileTree}
                        title="새로고침"
                    >
                        <RefreshCw class="w-4 h-4" />
                    </button>
                </div>
            </div>
            {#if fileTree}
                <div class="space-y-2">
                    <TreeNode node={fileTree} {expandedNodes} {toggleNode} />
                </div>
            {/if}
        </div>

        <div class="flex-1 space-y-4">
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <input
                    type="text"
                    bind:value={searchQuery}
                    on:input={searchFiles}
                    placeholder="파일 검색..."
                    class="w-full p-2 rounded border dark:bg-gray-700 dark:border-gray-600"
                />
                
                {#if searchResults.length > 0}
                    <div class="mt-4 space-y-2">
                        {#each searchResults as result}
                            <div class="flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                                {#if result.is_directory}
                                    <Folder class="w-4 h-4" />
                                {:else}
                                    <File class="w-4 h-4" />
                                {/if}
                                <span>{result.name}</span>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    </div>
</div>