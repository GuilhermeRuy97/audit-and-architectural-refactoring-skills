const express = require('express');
const AuthController = require('../controllers/authController');

const router = express.Router();

router.post('/register', async (req, res, next) => {
  try {
    const { name, email, password } = req.body;
    const result = await AuthController.register(name, email, password);
    res.status(201).json(result);
  } catch (err) {
    next(err);
  }
});

router.post('/login', async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const result = await AuthController.login(email, password);
    res.status(200).json(result);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
