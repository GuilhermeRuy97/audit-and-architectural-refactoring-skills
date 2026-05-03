const express = require('express');
const CheckoutController = require('../controllers/checkoutController');
const { requireAuth } = require('../middlewares/auth');

const router = express.Router();

router.post('/checkout', requireAuth, async (req, res, next) => {
  try {
    const { course_id: courseId, card } = req.body;
    if (!courseId || !card) {
      return res.status(400).json({ error: 'course_id and card are required' });
    }
    const result = await CheckoutController.processCheckout(req.user.sub, courseId, card);
    res.status(200).json({ msg: 'Success', enrollment_id: result.enrollmentId });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
