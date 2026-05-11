import axios from "axios";
import { ElMessage } from "element-plus";

const api = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || "请求失败";
    ElMessage.error(msg);
    return Promise.reject(err);
  }
);

export default api;

// 用户接口
export const userApi = {
  register: (data) => api.post("/users/register", data),
  login: (data) => api.post("/users/login", data),
  getUser: (id) => api.get(`/users/${id}`),
  updateProfile: (id, data) => api.patch(`/users/${id}`, data),
  changePassword: (id, data) => api.patch(`/users/${id}/password`, data),
  createTeam: (data, ownerId) => api.post(`/users/teams?owner_id=${ownerId}`, data),
  joinTeam: (code, userId) => api.post(`/users/teams/join?invite_code=${code}&user_id=${userId}`),
  getTeams: (userId) => api.get(`/users/${userId}/teams`),
  getTeam: (teamId) => api.get(`/teams/${teamId}`),
  getTeamMembers: (teamId) => api.get(`/teams/${teamId}/members`),
};

// 任务接口
export const taskApi = {
  list: (userId, params) => api.get("/tasks/", { params: { owner_id: userId, ...params } }),
  create: (data) => api.post("/tasks/", data),
  get: (id) => api.get(`/tasks/${id}`),
  update: (id, data) => api.patch(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
  checkin: (id) => api.post(`/tasks/${id}/checkin`),
  batchSort: (items) => api.patch("/tasks/batch-sort", items),
  createStudyRecord: (data) => api.post("/tasks/study-record", data),
};

// 评论接口
export const commentApi = {
  list: (taskId) => api.get(`/comments/task/${taskId}`),
  create: (data) => api.post("/comments/", data),
  delete: (id) => api.delete(`/comments/${id}`),
};

// 单词接口
export const vocabApi = {
  listBooks: (userId) => api.get("/vocabulary/books", { params: { user_id: userId } }),
  createBook: (data) => api.post("/vocabulary/books", data),
  listWords: (bookId) => api.get(`/vocabulary/books/${bookId}/words`),
  addWord: (bookId, data) => api.post(`/vocabulary/books/${bookId}/words`, data),
  batchAdd: (bookId, data) => api.post(`/vocabulary/books/${bookId}/words/batch`, data),
  getReview: (userId, limit) => api.get("/vocabulary/review", { params: { user_id: userId, limit } }),
  answer: (wordId, isCorrect) => api.post(`/vocabulary/words/${wordId}/answer`, { is_correct: isCorrect }),
  getErrors: (userId) => api.get("/vocabulary/error-words", { params: { user_id: userId } }),
  toggleStar: (wordId) => api.post(`/vocabulary/words/${wordId}/star`),
};

// 习惯接口
export const habitApi = {
  list: (userId) => api.get("/habits/", { params: { user_id: userId } }),
  create: (data) => api.post("/habits/", data),
  update: (id, data) => api.patch(`/habits/${id}`, data),
  delete: (id) => api.delete(`/habits/${id}`),
  checkin: (id) => api.post(`/habits/${id}/checkin`),
  getRecords: (habitId) => api.get(`/habits/${habitId}/records`),
  startPomodoro: (data) => api.post("/habits/pomodoro/start", data),
  completePomodoro: (id) => api.patch(`/habits/pomodoro/${id}/complete`),
  pomodoroHistory: (userId) => api.get("/habits/pomodoro/history", { params: { user_id: userId } }),
  leaderboard: () => api.get("/habits/leaderboard"),
};

// 统计接口
export const statsApi = {
  overview: (userId) => api.get("/stats/overview", { params: { user_id: userId } }),
  weeklyTasks: (userId) => api.get("/stats/weekly-tasks", { params: { user_id: userId } }),
  weeklyWords: (userId) => api.get("/stats/weekly-words", { params: { user_id: userId } }),
  masteryHeatmap: (userId) => api.get("/stats/word-mastery-heatmap", { params: { user_id: userId } }),
  teamComparison: (teamId) => api.get(`/stats/team-comparison/${teamId}`),
  weeklyPomodoro: (userId) => api.get("/stats/weekly-pomodoro", { params: { user_id: userId } }),
  habitStreak: (userId) => api.get("/stats/habit-streak", { params: { user_id: userId } }),
};

// 导出接口
export const exportApi = {
  weeklyReport: (userId) => api.get("/export/weekly-report", { params: { user_id: userId }, responseType: "blob" }),
};
