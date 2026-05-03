require('dotenv').config();

const config = {
  port: parseInt(process.env.PORT) || 3000,
  jwtSecret: process.env.JWT_SECRET || 'dev-only-insecure-secret-change-in-prod',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  dbPath: process.env.DB_PATH || ':memory:',
  saltRounds: parseInt(process.env.BCRYPT_SALT_ROUNDS) || 12,
  seedUserPassword: process.env.SEED_USER_PASSWORD || 'changeme',
};

if (process.env.NODE_ENV === 'production' && !process.env.JWT_SECRET) {
  throw new Error('JWT_SECRET environment variable is required in production');
}

module.exports = config;
