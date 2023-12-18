<template>
    <div class="image-container">
        <img v-if="imageUrl" :src="imageUrl" class="bear-image">
        <p v-if="metadata">{{ metadata.prompt }}</p>
    </div>
</template>

<script>
export default {
    name: 'BearImage',
    props: ['imageUrl', 'metadata']
}
</script>

<style scoped>
.image-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.bear-image {
    width: 40%;
    height: auto;
    border: none;
    box-shadow: 0px 10px 18px -7px rgba(0,0,0,0.75);
}

p {
    font-size: 1.2em;
    color: #777;
}
</style>