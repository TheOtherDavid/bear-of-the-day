<template>
    <div>
        <div v-for="(image, index) in images" :key="index">
            <img :src="image" alt="Bear image" />
        </div>
        <button @click="loadMore">Load more bears</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            images: [],
            offset: 1,
            size: 5
        }
    },
    methods: {
        loadMore() {
            fetch(process.env.VUE_APP_BACKEND_BATCH_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    size: this.size,
                    offset: this.offset
                })
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    this.images.push(...data.urls);
                    this.offset += this.size;
                });
        }
    }
}
</script>