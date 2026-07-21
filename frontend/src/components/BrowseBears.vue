<template>
    <div class="browse">
        <div class="filters">
            <label>
                Subject
                <select v-model="filters.subject">
                    <option value="">Any</option>
                    <option v-for="o in facets.subjects" :key="o.value" :value="o.value">
                        {{ o.value }} ({{ o.count }})
                    </option>
                </select>
            </label>
            <label>
                Scene
                <select v-model="filters.scene">
                    <option value="">Any</option>
                    <option v-for="o in facets.scenes" :key="o.value" :value="o.value">
                        {{ o.value }} ({{ o.count }})
                    </option>
                </select>
            </label>
            <label>
                Spirit
                <select v-model="filters.spirit">
                    <option value="">Any</option>
                    <option v-for="o in facets.spirits" :key="o.value" :value="o.value">
                        {{ o.value }} ({{ o.count }})
                    </option>
                </select>
            </label>
            <label>
                Prompt contains
                <input v-model="filters.prompt" type="text" placeholder="search text…">
            </label>
            <button class="reset" @click="resetFilters">Reset</button>
        </div>

        <p v-if="loading" class="status">Loading gallery…</p>
        <p v-else-if="error" class="status">Could not load the gallery: {{ error }}</p>
        <p v-else class="status">{{ filtered.length }} of {{ images.length }} bears</p>

        <div class="gallery">
            <BearImage
                v-for="entry in visible"
                :key="entry.key"
                :imageUrl="urls[entry.key]"
                :metadata="entry"
            />
        </div>

        <div v-if="visible.length < filtered.length" class="button-container">
            <button class="load-more-button" @click="loadMore">Load more bears</button>
        </div>
    </div>
</template>

<script>
import BearImage from './BearImage.vue'

const PAGE_SIZE = 12

// Endpoint URLs come from build-time env vars when set, with sensible defaults
// so the gallery works even where those vars aren't configured. (The repo-wide
// .gitignore excludes .env files, so defaults live here rather than in .env.)
const API_BASE = 'https://ly8ms91c44.execute-api.us-east-2.amazonaws.com/Prod'
const MANIFEST_URL = process.env.VUE_APP_MANIFEST_URL || `${API_BASE}/manifest`
const BEARURLS_URL = process.env.VUE_APP_BEARURLS_URL || `${API_BASE}/bearurls`

export default {
    name: 'BrowseBears',
    components: { BearImage },
    data() {
        return {
            images: [],
            urls: {},
            loading: true,
            error: null,
            visibleCount: PAGE_SIZE,
            filters: { subject: '', scene: '', spirit: '', prompt: '' },
        }
    },
    computed: {
        facets() {
            const tally = (values) => {
                const counts = {}
                for (const v of values) {
                    if (!v) continue
                    counts[v] = (counts[v] || 0) + 1
                }
                return Object.entries(counts)
                    .map(([value, count]) => ({ value, count }))
                    .sort((a, b) => b.count - a.count || a.value.localeCompare(b.value))
            }
            return {
                subjects: tally(this.images.map(e => e.subject)),
                scenes: tally(this.images.map(e => e.scene)),
                spirits: tally(this.images.flatMap(e => e.spirits || [])),
            }
        },
        filtered() {
            const { subject, scene, spirit, prompt } = this.filters
            const needle = prompt.trim().toLowerCase()
            return this.images.filter(e => {
                if (subject && e.subject !== subject) return false
                if (scene && e.scene !== scene) return false
                if (spirit && !(e.spirits || []).includes(spirit)) return false
                if (needle && !(e.prompt || '').toLowerCase().includes(needle)) return false
                return true
            })
        },
        visible() {
            return this.filtered.slice(0, this.visibleCount)
        },
        visibleKeys() {
            return this.visible.map(e => e.key)
        },
    },
    watch: {
        // Any filter change resets paging back to the first page.
        filters: {
            deep: true,
            handler() { this.visibleCount = PAGE_SIZE },
        },
        // Fetch presigned URLs for whatever is currently visible.
        visibleKeys: {
            immediate: true,
            handler(keys) { this.ensureUrls(keys) },
        },
    },
    created() {
        this.loadManifest()
    },
    methods: {
        async loadManifest() {
            try {
                const res = await fetch(MANIFEST_URL)
                if (!res.ok) throw new Error(`HTTP ${res.status}`)
                const data = await res.json()
                this.images = data.images || []
            } catch (e) {
                this.error = e.message
            } finally {
                this.loading = false
            }
        },
        async ensureUrls(keys) {
            const missing = keys.filter(k => !(k in this.urls))
            if (missing.length === 0) return
            try {
                const res = await fetch(BEARURLS_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ keys: missing }),
                })
                if (!res.ok) throw new Error(`HTTP ${res.status}`)
                const data = await res.json()
                this.urls = { ...this.urls, ...(data.urls || {}) }
            } catch (e) {
                console.error('Failed to fetch image URLs:', e)
            }
        },
        loadMore() {
            this.visibleCount += PAGE_SIZE
        },
        resetFilters() {
            this.filters = { subject: '', scene: '', spirit: '', prompt: '' }
        },
    },
}
</script>

<style scoped>
.filters {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: flex-end;
    justify-content: center;
    max-width: 900px;
    margin: 0 auto 10px;
    padding: 0 10px;
}

.filters label {
    display: flex;
    flex-direction: column;
    font-size: 0.9em;
    color: #555;
    gap: 4px;
}

.filters select,
.filters input {
    padding: 6px 8px;
    font-size: 1em;
    border: 1px solid #ccc;
    border-radius: 6px;
    max-width: 260px;
}

.reset {
    padding: 7px 14px;
    border: none;
    border-radius: 6px;
    background-color: #999;
    color: white;
    cursor: pointer;
}

.status {
    text-align: center;
    color: #777;
    margin: 8px 0;
}

.gallery {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.button-container {
    display: flex;
    justify-content: center;
    margin: 16px 0;
}

.load-more-button {
    padding: 10px 20px;
    font-size: 18px;
    background-color: #4CAF50;
    border: none;
    color: white;
    cursor: pointer;
    border-radius: 8px;
}
</style>
