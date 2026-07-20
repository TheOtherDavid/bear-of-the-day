<template>
    <BearImage :imageUrl="imageUrl" :metadata="metadata" />
</template>

<script>
import BearImage from './BearImage.vue'

// Fallback so the latest-bear panel works even where VUE_APP_BACKEND_URL isn't set.
const LATEST_BEAR_URL = process.env.VUE_APP_BACKEND_URL
    || 'https://ly8ms91c44.execute-api.us-east-2.amazonaws.com/Prod/bear'

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
        fetch(LATEST_BEAR_URL)
            .then(response => response.json())
            .then(data => {
                this.imageUrl = data.url;
                this.metadata = data.metadata;
            });
    }
}
</script>