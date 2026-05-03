const db = require('./db');

async function findActiveById(id) {
  return db.get('SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [id]);
}

async function findAll() {
  return db.all('SELECT id, title, price, active FROM courses', []);
}

module.exports = { findActiveById, findAll };
