import { createRouter, createWebHistory } from 'vue-router'
import { authState, initAuth } from '../store/auth'
import Home from '../views/Home.vue'
import ConsoleStartView from '../views/ConsoleStartView.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    redirect: to => ({
      name: 'Home',
      query: {
        auth: 'signin',
        ...(typeof to.query.redirect === 'string' ? { redirect: to.query.redirect } : {})
      }
    })
  },
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/console',
    name: 'ConsoleStart',
    component: ConsoleStartView
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async to => {
  await initAuth()

  if (to.name === 'Home' || to.name === 'Login') {
    return true
  }

  if (!authState.user) {
    return {
      name: 'Login',
      query: {
        redirect: to.fullPath
      }
    }
  }

  return true
})

export default router
