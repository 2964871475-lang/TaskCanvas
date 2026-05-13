import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useUserStore = defineStore("user", () => {
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"));

  const isLoggedIn = computed(() => !!user.value);
  const userId = computed(() => user.value?.id);
  const username = computed(() => user.value?.username || "");
  const isAdmin = computed(() => !!user.value?.is_admin);

  function setUser(data) {
    user.value = data;
    localStorage.setItem("user", JSON.stringify(data));
  }

  function logout() {
    user.value = null;
    localStorage.removeItem("user");
  }

  function updateProfile(fields) {
    if (user.value) {
      user.value = { ...user.value, ...fields };
      localStorage.setItem("user", JSON.stringify(user.value));
    }
  }

  return { user, isLoggedIn, userId, username, isAdmin, setUser, logout, updateProfile };
});
