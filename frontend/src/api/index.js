import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

export default api;

// 用户接口
export const userApi = {
  register: (data) => api.post("/users/register", data),
  login: (data) => api.post("/users/login", data),
  getUser: (id) => api.get(`/users/${id}`),
  createTeam: (data, ownerId) => api.post(`/users/teams?owner_id=${ownerId}`, data),
  joinTeam: (code, userId) => api.post(`/users/teams/join?invite_code=${code}&user_id=${userId}`),
};

// 任务接口
export const taskApi = {
  list: (userId, params) => api.get("/tasks/", { params: { owner_id: userId, ...params } }),
  create: (data) => api.post("/tasks/", data),
  get: (id) => api.get(`/tasks/${id}`),
  update: (id, data) => api.patch(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
  checkin: (id) => api.post(`/tasks/${id}/checkin`),
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
};

// 习惯接口
export const habitApi = {
  list: (userId) => api.get("/habits/", { params: { user_id: userId } }),
  create: (data) => api.post("/habits/", data),
  checkin: (id) => api.post(`/habits/${id}/checkin`),
  startPomodoro: (data) => api.post("/habits/pomodoro/start", data),
  completePomodoro: (id) => api.patch(`/habits/pomodoro/${id}/complete`),
  leaderboard: () => api.get("/habits/leaderboard"),
};

// 统计接口
export const statsApi = {
  overview: (userId) => api.get("/stats/overview", { params: { user_id: userId } }),
  weeklyTasks: (userId) => api.get("/stats/weekly-tasks", { params: { user_id: userId } }),
  weeklyWords: (userId) => api.get("/stats/weekly-words", { params: { user_id: userId } }),
  masteryHeatmap: (userId) => api.get("/stats/word-mastery-heatmap", { params: { user_id: userId } }),
};
