import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initAuth } from './store/auth'
import './styles/opsTheme.css'

const app = createApp(App)

app.use(router)

initAuth().finally(() => {
  app.mount('#app')
})
