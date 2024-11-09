<script>
    import { ChevronRight, ChevronDown, Folder, File } from 'lucide-svelte';
    
    export let node;
    export let expandedNodes;
    export let toggleNode;
    export let depth = 0;

    $: isExpanded = expandedNodes.has(node.uuid);
</script>

<div style="margin-left: {depth * 1.5}rem">
    <button
        type="button"
        class="flex items-center gap-2 p-2 w-full text-left hover:bg-gray-100 dark:hover:bg-gray-700 rounded cursor-pointer"
        on:click={() => toggleNode(node.uuid)}
        on:keydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleNode(node.uuid);
            }
        }}
    >
        {#if node.is_directory}
            {#if isExpanded}
                <ChevronDown class="w-4 h-4" />
            {:else}
                <ChevronRight class="w-4 h-4" />
            {/if}
            <Folder class="w-4 h-4" />
        {:else}
            <File class="w-4 h-4" />
        {/if}
        <span>{node.name}</span>
    </button>
    
    {#if node.is_directory && isExpanded}
        <div class="ml-4">
            {#each node.children as child}
                <svelte:self 
                    node={child}
                    {expandedNodes}
                    {toggleNode}
                    depth={depth + 1}
                />
            {/each}
        </div>
    {/if}
</div>