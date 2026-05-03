const db = require('./db');

async function create(userId, courseId) {
  const result = await db.run(
    'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    [userId, courseId]
  );
  return result.lastID;
}

async function findByCourseId(courseId) {
  return db.all('SELECT id, user_id, course_id FROM enrollments WHERE course_id = ?', [courseId]);
}

module.exports = { create, findByCourseId };
