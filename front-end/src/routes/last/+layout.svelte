<script>
    import { 
        Computer, Download, File, Folder,
        Images, List, ListOrdered, Music, Video, View
    } from 'lucide-svelte';
    
    let darkMode = false;
</script>

<div class="grid min-h-screen w-full lg:grid-cols-[280px_1fr]">
    <!-- Sidebar -->
    <div class="hidden border-r bg-gray-100/40 lg:block {darkMode ? 'dark:bg-gray-800/40' : ''}">
        <div class="flex h-full max-h-screen flex-col gap-2">
            <div class="flex h-[60px] items-center border-b px-6">
                <a href="/" class="flex items-center gap-2 font-semibold">
                    <Folder class="h-6 w-6" />
                    <span>Finder</span>
                </a>
            </div>
            <div class="flex-1 overflow-auto py-2">
                <nav class="grid items-start px-4 text-sm font-medium">
                    {#each [
                        { icon: Computer, label: 'Desktop' },
                        { icon: File, label: 'Documents' },
                        { icon: Download, label: 'Downloads' },
                        { icon: Images, label: 'Pictures' },
                        { icon: Music, label: 'Music' },
                        { icon: Video, label: 'Videos' }
                    ] as item}
                        <a
                            href="/"
                            class="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900 {darkMode ? 'dark:text-gray-400 dark:hover:text-gray-50' : ''}"
                        >
                            <svelte:component this={item.icon} class="h-4 w-4" />
                            {item.label}
                        </a>
                    {/each}
                </nav>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="flex flex-col">
        <header class="flex h-14 lg:h-[60px] items-center gap-4 border-b bg-gray-100/40 px-6 {darkMode ? 'dark:bg-gray-800/40' : ''}">
            <!-- Action Buttons -->
            <div class="flex items-center gap-2 ml-auto">
                <button class="p-2 rounded-lg bg-gray-200 {darkMode ? 'dark:bg-gray-700' : ''}" aria-label="View as list">
                    <List class="h-5 w-5" />
                </button>
                <button class="p-2 rounded-lg" aria-label="View as grid">
                    <View class="h-5 w-5" />
                </button>
                <button class="p-2 rounded-lg" aria-label="Sort">
                    <ListOrdered class="h-5 w-5" />
                </button>
            </div>
        </header>

        <slot />
    </div>
</div>

<style>
    :global(.dark) {
        color-scheme: dark;
    }
</style>