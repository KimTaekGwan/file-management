<script>
    import { onMount } from 'svelte';
    import TreeNode from '$lib/components/TreeNode.svelte';
    import { Folder, File, RefreshCw } from 'lucide-svelte';
    
    let fileTree = null;
    let expandedNodes = new Set();
    let searchQuery = '';
    let searchResults = [];
    let autoRefresh = false;
    let refreshInterval = null;

    async function fetchFileTree() {
        try {
            const response = await fetch('http://localhost:8000/api/filesystem/tree');
            fileTree = await response.json();
            console.log('파일 트리 새로고침 완료');
        } catch (error) {
            console.error('파일 트리 가져오기 실패:', error);
        }
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
        expandedNodes = expandedNodes; // Svelte 반응성 트리거
    }

    function toggleAutoRefresh() {
        autoRefresh = !autoRefresh;
        
        if (autoRefresh) {
            console.log('자동 새로고침 시작');
            refreshInterval = setInterval(async () => {
                await fetchFileTree();
            }, 5000);
        } else {
            console.log('자동 새로고침 중지');
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        }
    }

    onMount(() => {
        fetchFileTree();
        
        return () => {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        };
    });
</script>

<div class="container mx-auto p-4">
    <div class="flex gap-4">
        <!-- 파일 트리 -->
        <div class="w-1/3 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div class="mb-4 flex justify-between items-center">
                <h2 class="text-lg font-semibold">파일 시스템</h2>
                <div class="flex items-center gap-2">
                    <button
                        class="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                        on:click={fetchFileTree}
                        title="새로고침"
                    >
                        <RefreshCw class="w-4 h-4" />
                    </button>
                    <button
                        class="px-3 py-1 rounded text-sm {autoRefresh 
                            ? 'bg-blue-500 text-white hover:bg-blue-600' 
                            : 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600'}"
                        on:click={toggleAutoRefresh}
                    >
                        {autoRefresh ? '자동 새로고침 켜짐' : '자동 새로고침'}
                    </button>
                </div>
            </div>
            {#if fileTree}
                <div class="space-y-2">
                    <TreeNode node={fileTree} {expandedNodes} {toggleNode} />
                </div>
            {/if}
        </div>

        <!-- 검색 및 상세 정보 -->
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