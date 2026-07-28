<template>
    <div class="image-container">
        <img v-if="imageUrl" :src="imageUrl" class="bear-image" loading="lazy" decoding="async">
        <div v-if="metadata" class="bear-details">
            <time v-if="formattedDate" class="bear-date" :datetime="metadata.timestamp">
                {{ formattedDate }}
            </time>
            <p v-if="metadata.prompt" class="bear-prompt">{{ metadata.prompt }}</p>
        </div>
    </div>
</template>

<script>
export default {
    name: 'BearImage',
    props: {
        imageUrl: { type: String, default: '' },
        metadata: { type: Object, default: null },
    },
    computed: {
        formattedDate() {
            if (!this.metadata || !this.metadata.timestamp) return ''

            const date = new Date(this.metadata.timestamp)
            if (Number.isNaN(date.getTime())) return ''

            return new Intl.DateTimeFormat(undefined, {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                timeZone: 'UTC',
            }).format(date)
        },
    },
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

.bear-details {
    width: 40%;
    text-align: center;
}

.bear-date {
    display: block;
    margin-top: 14px;
    font-size: 1em;
    font-weight: 600;
    color: #555;
}

.bear-prompt {
    margin: 6px 0 0;
    font-size: 1.2em;
    color: #777;
}
</style>