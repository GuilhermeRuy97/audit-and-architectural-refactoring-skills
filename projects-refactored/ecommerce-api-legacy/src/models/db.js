const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');
const config = require('../config');

const rawDb = new sqlite3.Database(config.dbPath);

rawDb.run('PRAGMA foreign_keys = ON');

const db = {
  get: promisify(rawDb.get.bind(rawDb)),
  all: promisify(rawDb.all.bind(rawDb)),
  run: (sql, params = []) =>
    new Promise((resolve, reject) =>
      rawDb.run(sql, params, function (err) {
        err ? reject(err) : resolve(this);
      })
    ),
};

module.exports = db;
