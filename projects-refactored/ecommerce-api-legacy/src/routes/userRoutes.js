const express = require('express');
const UserModel = require('../models/userModel');
const { requireAuth, requireAdmin } = require('../middlewares/auth');

const router = express.Router();

router.delete('/users/:id', requireAuth, requireAdmin, async (req, res, next) => {
  try {
    const userId = parseInt(req.params.id, 10);
    if (isNaN(userId)) {
      return res.status(400).json({ error: 'Invalid user ID' });
    }
    const user = await UserModel.findById(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    await UserModel.deleteById(userId);
    res.status(200).json({ msg: 'User and related records deleted successfully' });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
