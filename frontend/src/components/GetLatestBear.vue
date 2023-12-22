<template>
    <BearImage :imageUrl="imageUrl" :metadata="metadata" />
</template>

<script>
import BearImage from './BearImage.vue'

export default {
    name: 'GetLatestBear',
    components: {
        BearImage
    },
    data() {
        return {
            imageUrl: null,
            metadata: null
        }
    },
    created() {
        fetch(process.env.VUE_APP_BACKEND_URL)
            .then(response => response.json())
            .then(data => {
                this.imageUrl = data.url;
                this.metadata = data.metadata;
            });
    }
}
</script>