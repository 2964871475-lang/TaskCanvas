import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/", name: "Home", component: () => import("../views/Home.vue") },
  { path: "/login", name: "Login", component: () => import("../views/Login.vue") },
  { path: "/tasks", name: "Tasks", component: () => import("../views/Tasks.vue") },
  { path: "/vocabulary", name: "Vocabulary", component: () => import("../views/Vocabulary.vue") },
  { path: "/habits", name: "Habits", component: () => import("../views/Habits.vue") },
  { path: "/dashboard", name: "Dashboard", component: () => import("../views/Dashboard.vue") },
  { path: "/team", name: "Team", component: () => import("../views/Team.vue") },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
