<template>
  <div id="content">
    <h1>Bear Of The Day!</h1>
    <GetLatestBear />
    <LoadMoreBears />
  </div>
</template>

<script>
import GetLatestBear from './components/GetLatestBear.vue'
import LoadMoreBears from './components/LoadMoreBears.vue'
export default {
  name: 'App',
  components: {
    GetLatestBear,
    LoadMoreBears
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: #f4f4f4;
  font-family: 'Roboto', sans-serif;
}

#app {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  color: #333;
}

#content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: auto;
  overflow: auto
}

h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
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
