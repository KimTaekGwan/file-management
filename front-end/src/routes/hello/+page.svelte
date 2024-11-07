<!-- Finder.svelte -->
<script>
    // Icons are imported from an icon library of your choice
    import { 
      ChevronRight,
      Computer,
      Download,
      File,
      Folder,
      Home,
      Images,
      List,
      ListOrdered,
      MoveHorizontal,
      Music,
      Plus,
      Video,
      View
    } from 'lucide-svelte';
  
    // Props
    export let darkMode = false;
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
        <!-- Breadcrumb -->
        <nav class="flex" aria-label="Breadcrumb">
          <ol class="flex items-center gap-2">
            <li>
              <a href="/" class="flex items-center">
                <Home class="h-4 w-4" />
              </a>
            </li>
            <li>
              <ChevronRight class="h-4 w-4" />
            </li>
            <li>
              <a href="/documents">Documents</a>
            </li>
            <li>
              <ChevronRight class="h-4 w-4" />
            </li>
            <li>
              <span class="text-gray-500">Project Files</span>
            </li>
          </ol>
        </nav>
  
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
          <button class="p-2 rounded-lg" aria-label="Add Folder">
            <Plus class="h-5 w-5" />
          </button>
        </div>
      </header>
  
      <!-- File List -->
      <main class="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-6">
        <div class="grid gap-2">
          {#each [
            { type: 'folder', name: 'Project Files', items: '12 items' },
            { type: 'file', name: 'report.pdf', size: '2.3 MB' },
            { type: 'file', name: 'presentation.pptx', size: '4.5 MB' },
            { type: 'file', name: 'spreadsheet.xlsx', size: '1.7 MB' },
            { type: 'folder', name: '한국어가 이상한건가Design Assets', items: '24 items' },
            { type: 'file', name: 'image.jpg', size: '1.2 MB' },
            { type: 'file', name: 'document.docx', size: '3.4 MB' },
            { type: 'folder', name: 'Archives', items: '8 items' }
          ] as item}
            <div class="flex items-center gap-4 rounded-lg bg-gray-100 {darkMode ? 'dark:bg-gray-800' : ''} hover:bg-gray-200 {darkMode ? 'dark:hover:bg-gray-700' : ''} transition-colors p-3">
              <svelte:component 
                this={item.type === 'folder' ? Folder : File} 
                class="h-8 w-8 {item.type === 'folder' ? 'text-primary' : 'text-gray-500 dark:text-gray-400'}" 
              />
              <div class="flex-1">
                <div class="text-sm font-medium truncate">{item.name}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{item.type === 'folder' ? item.items : item.size}</div>
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
    </div>
  </div>
  
  <style>
    /* Add any additional scoped styles here */
    :global(.dark) {
      color-scheme: dark;
    }
  </style>