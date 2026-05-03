const db = require('./db');

async function create(enrollmentId, amount, status) {
  const result = await db.run(
    'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    [enrollmentId, amount, status]
  );
  return result.lastID;
}

async function findByEnrollmentId(enrollmentId) {
  return db.get(
    'SELECT id, amount, status FROM payments WHERE enrollment_id = ?',
    [enrollmentId]
  );
}

module.exports = { create, findByEnrollmentId };
