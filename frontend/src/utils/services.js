import api from './api'

/**
 * 获取教师列表
 * @returns {Promise<Array>} 教师列表
 */
export const getTeachers = async () => {
  try {
    const response = await api.get('/users')
    // 只保留具有教师角色的用户
    return (response.data || []).filter(user => {
      return user.roles && user.roles.some(role => role.name === '教师')
    })
  } catch (error) {
    console.error('获取教师列表失败:', error)
    return []
  }
}
