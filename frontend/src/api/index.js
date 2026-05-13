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
  getAnnouncements: (userId) => api.get("/announcements", { params: { user_id: userId || 0 } }),
  getTeam: (teamId) => api.get(`/teams/${teamId}`),
  getTeamMembers: (teamId) => api.get(`/teams/${teamId}/members`),
  deleteTeam: (teamId, userId) => api.delete(`/teams/${teamId}`, { params: { user_id: userId } }),
  removeMember: (teamId, memberId, operatorId) => api.delete(`/teams/${teamId}/members/${memberId}`, { params: { operator_id: operatorId } }),
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
  batchDelete: (ids) => api.post("/tasks/batch-delete", { ids }),
  createStudyRecord: (data) => api.post("/tasks/study-record", data),
  export: (userId) => api.get(`/tasks/export/${userId}`),
  import: (userId, formData) => api.post(`/tasks/import/${userId}`, formData, { headers: { "Content-Type": "multipart/form-data" } }),
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
  getReviewCount: (userId) => api.get("/vocabulary/review-count", { params: { user_id: userId } }),
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
  dailyProgress: (userId) => api.get("/stats/daily-progress", { params: { user_id: userId } }),
  listGoals: (userId) => api.get("/stats/study-goals", { params: { user_id: userId } }),
  createGoal: (data) => api.post("/stats/study-goals", data),
  deleteGoal: (goalId) => api.delete(`/stats/study-goals/${goalId}`),
};

// 导出接口
export const exportApi = {
  weeklyReport: (userId) => api.get("/export/weekly-report", { params: { user_id: userId }, responseType: "blob" }),
  dailyReport: (userId) => api.get("/export/daily-report", { params: { user_id: userId } }),
  monthlyReport: (userId) => api.get("/export/monthly-report", { params: { user_id: userId } }),
};

// 管理员接口
export const adminApi = {
  listUsers: (operatorId) => api.get("/admin/users", { params: { operator_id: operatorId } }),
  toggleDisable: (userId, operatorId) => api.patch(`/admin/users/${userId}/toggle-disable`, null, { params: { operator_id: operatorId } }),
  resetPassword: (userId, operatorId) => api.post(`/admin/users/${userId}/reset-password`, null, { params: { operator_id: operatorId } }),
  deleteUser: (userId, operatorId) => api.delete(`/admin/users/${userId}`, { params: { operator_id: operatorId } }),
  stats: (operatorId) => api.get("/admin/stats", { params: { operator_id: operatorId } }),
  listTeams: (operatorId) => api.get("/admin/teams", { params: { operator_id: operatorId } }),
  teamMembers: (teamId, operatorId) => api.get(`/admin/teams/${teamId}/members`, { params: { operator_id: operatorId } }),
  teamStats: (teamId, operatorId) => api.get(`/admin/teams/${teamId}/stats`, { params: { operator_id: operatorId } }),
  transferOwner: (teamId, newOwnerId, operatorId) => api.patch(`/admin/teams/${teamId}/transfer`, null, { params: { new_owner_id: newOwnerId, operator_id: operatorId } }),
  removeMember: (teamId, userId, operatorId) => api.delete(`/admin/teams/${teamId}/members/${userId}`, { params: { operator_id: operatorId } }),
  dissolveTeam: (teamId, operatorId) => api.delete(`/admin/teams/${teamId}`, { params: { operator_id: operatorId } }),
  listAnnouncements: (operatorId) => api.get("/admin/announcements", { params: { operator_id: operatorId } }),
  createAnnouncement: (data, operatorId) => api.post("/admin/announcements", data, { params: { operator_id: operatorId } }),
  deleteAnnouncement: (annId, operatorId) => api.delete(`/admin/announcements/${annId}`, { params: { operator_id: operatorId } }),
  exportData: (operatorId) => api.get("/admin/export", { params: { operator_id: operatorId } }),
  listLogs: (operatorId, page, size) => api.get("/admin/logs", { params: { operator_id: operatorId, page, size } }),
  logsCount: (operatorId) => api.get("/admin/logs/count", { params: { operator_id: operatorId } }),
};
