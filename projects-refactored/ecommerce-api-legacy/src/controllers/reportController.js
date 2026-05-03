const db = require('../models/db');

async function getFinancialReport() {
  const rows = await db.all(`
    SELECT
      c.id   AS courseId,
      c.title,
      u.name AS studentName,
      p.amount,
      p.status
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users u       ON u.id = e.user_id
    LEFT JOIN payments p    ON p.enrollment_id = e.id
    ORDER BY c.id
  `, []);

  const coursesMap = {};
  for (const row of rows) {
    if (!coursesMap[row.courseId]) {
      coursesMap[row.courseId] = { course: row.title, revenue: 0, students: [] };
    }
    if (row.studentName) {
      if (row.status === 'PAID') {
        coursesMap[row.courseId].revenue += row.amount;
      }
      coursesMap[row.courseId].students.push({
        student: row.studentName,
        paid: row.amount || 0,
      });
    }
  }

  return Object.values(coursesMap);
}

module.exports = { getFinancialReport };
