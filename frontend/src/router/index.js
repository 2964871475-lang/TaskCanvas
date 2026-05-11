import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/", name: "Home", component: () => import("../views/Home.vue") },
  { path: "/login", name: "Login", component: () => import("../views/Login.vue") },
  { path: "/tasks", name: "Tasks", component: () => import("../views/Tasks.vue"), meta: { requiresAuth: true } },
  { path: "/vocabulary", name: "Vocabulary", component: () => import("../views/Vocabulary.vue"), meta: { requiresAuth: true } },
  { path: "/habits", name: "Habits", component: () => import("../views/Habits.vue"), meta: { requiresAuth: true } },
  { path: "/dashboard", name: "Dashboard", component: () => import("../views/Dashboard.vue"), meta: { requiresAuth: true } },
  { path: "/team", name: "Team", component: () => import("../views/Team.vue"), meta: { requiresAuth: true } },
  { path: "/profile", name: "Profile", component: () => import("../views/Profile.vue"), meta: { requiresAuth: true } },
  { path: "/:pathMatch(.*)*", name: "NotFound", component: () => import("../views/NotFound.vue") },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const user = localStorage.getItem("user");
    if (!user) {
      next({ path: "/login", query: { redirect: to.fullPath } });
      return;
    }
  }
  next();
});

export default router;
