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
    path: '/demo',
    name: 'DemoIntake',
    component: ConsoleStartView,
    meta: { public: true }
  },
  {
    path: '/demo/graph',
    name: 'DemoGraph',
    component: Process,
    meta: { public: true }
  },
  {
    path: '/demo/population',
    name: 'DemoPopulation',
    component: SimulationView,
    meta: { public: true }
  },
  {
    path: '/demo/simulation',
    name: 'DemoSimulation',
    component: SimulationRunView,
    meta: { public: true }
  },
  {
    path: '/demo/report',
    name: 'DemoReport',
    component: ReportView,
    meta: { public: true }
  },
  {
    path: '/demo/interaction',
    name: 'DemoInteraction',
    component: InteractionView,
    meta: { public: true }
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

// Opt-in, local-only escape hatch: lets a developer open stored runs
// (/simulation/:id, /report/:id, ...) on a machine with no reachable Supabase
// auth backend. Off unless VITE_LOCAL_AUTH_BYPASS is explicitly "true", so
// hosted builds keep the normal sign-in requirement.
const localAuthBypass = import.meta.env.VITE_LOCAL_AUTH_BYPASS === 'true'

router.beforeEach(async to => {
  await initAuth()

  if (to.name === 'Home' || to.name === 'Login' || to.meta.public || to.path.startsWith('/demo')) {
    return true
  }

  if (localAuthBypass) {
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
