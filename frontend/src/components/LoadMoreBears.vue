<template>
    <div>
        <div v-for="(image, index) in images" :key="index">
            <BearImage :imageUrl="image.url" :metadata="image.metadata" />
        </div>
        <button @click="loadMore">Load more bears</button>
    </div>
</template>

<script>
import BearImage from './BearImage.vue'

export default {
    name: 'LoadMoreBears',
    components: {
        BearImage
    },
    data() {
        return {
            images: [],
            offset: 1,
            size: 2
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
                    this.images.push(...data.images);
                    this.offset += this.size;
                });
        }
    }
}
</script>