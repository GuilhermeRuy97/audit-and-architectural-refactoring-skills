const bcrypt = require('bcrypt');
const db = require('./db');
const config = require('../config');

async function findByEmail(email) {
  return db.get('SELECT id, name, email, pass, role FROM users WHERE email = ?', [email]);
}

async function findById(id) {
  return db.get('SELECT id, name, email, role FROM users WHERE id = ?', [id]);
}

async function create(name, email, password, role = 'student') {
  const passwordHash = await bcrypt.hash(password, config.saltRounds);
  const result = await db.run(
    'INSERT INTO users (name, email, pass, role) VALUES (?, ?, ?, ?)',
    [name, email, passwordHash, role]
  );
  return result.lastID;
}

async function verifyPassword(plaintext, hash) {
  return bcrypt.compare(plaintext, hash);
}

async function deleteById(id) {
  await db.run(
    'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
    [id]
  );
  await db.run('DELETE FROM enrollments WHERE user_id = ?', [id]);
  await db.run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, findById, create, verifyPassword, deleteById };
