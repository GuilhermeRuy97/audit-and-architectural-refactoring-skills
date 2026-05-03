const express = require('express');
const ReportController = require('../controllers/reportController');
const { requireAuth, requireAdmin } = require('../middlewares/auth');

const router = express.Router();

router.get('/admin/financial-report', requireAuth, requireAdmin, async (req, res, next) => {
  try {
    const report = await ReportController.getFinancialReport();
    res.status(200).json(report);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
