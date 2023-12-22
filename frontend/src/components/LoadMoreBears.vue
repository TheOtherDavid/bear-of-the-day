<template>
    <div>
        <div v-for="(image, index) in images" :key="index">
            <BearImage :imageUrl="image.url" :metadata="image.metadata" />
        </div>
        <div class="button-container">
            <button class="load-more-button" @click="loadMore">Load more bears</button>
        </div>
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

<style scoped>
.button-container {
    display: flex;
    justify-content: center;
}

.load-more-button {
    padding: 10px 20px;
    font-size: 18px;
    background-color: #4CAF50; /* Green */
    border: none;
    color: white;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 8px;
}
</style>