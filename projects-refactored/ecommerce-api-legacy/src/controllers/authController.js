const jwt = require('jsonwebtoken');
const UserModel = require('../models/userModel');
const config = require('../config');

class AuthError extends Error {
  constructor(message) { super(message); this.name = 'AuthError'; }
}

class ValidationError extends Error {
  constructor(message) { super(message); this.name = 'ValidationError'; }
}

async function register(name, email, password) {
  if (!name || !email || !password) {
    throw new ValidationError('name, email and password are required');
  }
  const existing = await UserModel.findByEmail(email);
  if (existing) {
    throw new ValidationError('Email already in use');
  }
  const userId = await UserModel.create(name, email, password);
  return { userId };
}

async function login(email, password) {
  if (!email || !password) {
    throw new ValidationError('email and password are required');
  }
  const user = await UserModel.findByEmail(email);
  if (!user) {
    throw new AuthError('Invalid credentials');
  }
  const valid = await UserModel.verifyPassword(password, user.pass);
  if (!valid) {
    throw new AuthError('Invalid credentials');
  }
  const token = jwt.sign(
    { sub: user.id, role: user.role },
    config.jwtSecret,
    { expiresIn: '8h' }
  );
  return { token };
}

module.exports = { register, login, AuthError, ValidationError };
